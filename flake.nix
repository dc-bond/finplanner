{

  description = "financial planning application";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    {
      nixosModules.default = { config, lib, pkgs, ... }: 
        with lib;
        let
          cfg = config.services.finplanner;
        in {
          options.services.finplanner = {
            enable = mkEnableOption "financial planning application";
            
            port = mkOption {
              type = types.port;
              default = 8501;
              description = "port to listen on";
            };
            
            address = mkOption {
              type = types.str;
              default = "127.0.0.1";
              description = "address to bind to";
            };
            
            openFirewall = mkOption {
              type = types.bool;
              default = false;
              description = "whether to open the firewall port";
            };
          };
          
          config = mkIf cfg.enable {
            systemd.services.finplanner = {
              description = "financial planning application";
              wantedBy = [ "multi-user.target" ];
              after = [ "network.target" ];
              
              environment = {
                HOME = "/tmp/finplanner-home";
                STREAMLIT_SERVER_HEADLESS = "true";
                STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false";
              };
              
              serviceConfig = {
                ExecStartPre = "${pkgs.coreutils}/bin/mkdir -p /tmp/finplanner-home";
                ExecStart = ''${self.packages.${pkgs.system}.finplanner}/bin/finplanner \
                  --server.port=${toString cfg.port} \
                  --server.address=${cfg.address}'';
                Restart = "always";
                RestartSec = "10";
                DynamicUser = true;
                PrivateTmp = true;
                ProtectSystem = "strict";
                ProtectHome = true;
                NoNewPrivileges = true;
                RuntimeDirectory = "finplanner";
                RuntimeDirectoryMode = "0755";
                StateDirectory = "finplanner";
                StateDirectoryMode = "0755";
              };
            };
            
            networking.firewall.allowedTCPPorts = mkIf cfg.openFirewall [ cfg.port ];
          };
        };
    } // flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        python = pkgs.python311;
        
        finplanner = pkgs.stdenv.mkDerivation rec {
          pname = "finplanner";
          version = "1.0.1";
          
          src = ./.;
          
          nativeBuildInputs = [ pkgs.makeWrapper ];
          buildInputs = [ python pkgs.cacert ];
          
          dontBuild = true;
          
          installPhase = ''
            runHook preInstall
            
            mkdir -p $out/share/finplanner
            mkdir -p $out/lib/python
            
            # copy application files
            cp -r . $out/share/finplanner/
            
            # install Python dependencies using pip
            export HOME=$TMPDIR
            ${python}/bin/pip install \
              --no-cache-dir \
              --prefix=$out \
              --no-warn-script-location \
              -r $out/share/finplanner/requirements.txt
            
            # create wrapper script
            makeWrapper ${python}/bin/streamlit $out/bin/finplanner \
              --add-flags "run" \
              --add-flags "$out/share/finplanner/app.py" \
              --add-flags "--server.headless=true" \
              --add-flags "--browser.gatherUsageStats=false" \
              --set PYTHONPATH "$out/lib/python3.11/site-packages:$out/share/finplanner" \
              --set HOME "/tmp"
            
            runHook postInstall
          '';
          
          meta = with pkgs.lib; {
            description = "Financial Planning Application";
            license = licenses.mit;
            platforms = platforms.unix;
            mainProgram = "finplanner";
          };
        };
        
        # dev environment with pip-installed packages
        pythonWithPackages = python.withPackages (ps: with ps; [
          pip
          ipython
          black
          pylint
        ]);
        
      in {

        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonWithPackages ];
          
          shellHook = ''
            echo ""
            echo "Finplanner development environment activated"
            echo "Python version: $(python --version)"
            echo ""
            echo "Available commands:"
            echo "  streamlit run app.py   - Launch web app"
            echo "  ipython                - Interactive Python shell"
            echo "  black .                - Format code"
            echo "  pylint *.py            - Lint code"
            echo ""
            
            # set environment variables for development
            export PYTHONPATH="$PWD:$PYTHONPATH"
            export STREAMLIT_CONFIG_DIR="$PWD/.streamlit"
            
            # ensure config directory exists
            mkdir -p .streamlit
            
            # create config.toml if it doesn't exist
            if [ ! -f .streamlit/config.toml ] && [ -f config.toml ]; then
              cp config.toml .streamlit/
            fi
            
            # install requirements if not already installed
            if [ ! -d "venv" ]; then
              echo "Creating virtual environment..."
              python -m venv venv
              source venv/bin/activate
              pip install -r requirements.txt
              echo "Dependencies installed in venv/"
            else
              echo "Virtual environment exists. Activate with: source venv/bin/activate"
            fi
          '';
        };
        
        packages = {
          default = finplanner;
          finplanner = finplanner;
        };
        
        # app for `nix run`
        apps.default = flake-utils.lib.mkApp {
          drv = finplanner;
        };
      }
    );
}