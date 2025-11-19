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
        
        pythonOverrides = pkgs.python311.override {
          packageOverrides = self: super: {
            streamlit = super.streamlit.overridePythonAttrs (old: { doCheck = false; });
            sqlframe = super.sqlframe.overridePythonAttrs (old: { doCheck = false; });
            narwhals = super.narwhals.overridePythonAttrs (old: { doCheck = false; });
            polars = super.polars.overridePythonAttrs (old: { doCheck = false; });
          };
        };
        
        pythonEnv = pythonOverrides.withPackages (ps: with ps; [
          streamlit
          numpy
          pandas
          matplotlib
          scipy
        ]);
        
        finplanner = pkgs.stdenv.mkDerivation rec {
          pname = "finplanner";
          version = "1.0.1";
          
          src = ./.;
          
          nativeBuildInputs = [ pkgs.makeWrapper ];
          buildInputs = [ pythonEnv ];
          
          dontBuild = true;
          
          installPhase = ''
            runHook preInstall
            
            mkdir -p $out/share/finplanner
            mkdir -p $out/bin
            
            # copy application files
            cp -r . $out/share/finplanner/
            
            # create wrapper script
            makeWrapper ${pythonEnv}/bin/streamlit $out/bin/finplanner \
              --add-flags "run" \
              --add-flags "$out/share/finplanner/app.py" \
              --add-flags "--server.headless=true" \
              --add-flags "--browser.gatherUsageStats=false" \
              --set PYTHONPATH "$out/share/finplanner:${pythonEnv}/${pythonEnv.sitePackages}" \
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
        
        pythonDevEnv = python.withPackages (ps: with ps; [
          pip
          ipython
          black
          pylint
        ]);
        
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonDevEnv ];
          
          shellHook = ''
            echo ""
            echo "Financial planning development environment activated"
            echo "Python version: $(python --version)"
            echo ""
            echo "Available commands:"
            echo "  streamlit run app.py   - Launch web app"
            echo "  ipython                - Interactive Python shell"
            echo "  black .                - Format code"
            echo "  pylint *.py            - Lint code"
            echo ""
            
            export PYTHONPATH="$PWD:$PYTHONPATH"
            export STREAMLIT_CONFIG_DIR="$PWD/.streamlit"
            
            mkdir -p .streamlit
            
            if [ ! -f .streamlit/config.toml ] && [ -f config.toml ]; then
              cp config.toml .streamlit/
            fi
            
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
        
        apps.default = flake-utils.lib.mkApp {
          drv = finplanner;
        };
      }
    );
}