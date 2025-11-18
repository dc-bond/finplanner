{

  description = "Financial planning application";

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
            enable = mkEnableOption "Financial planning application";
            
            port = mkOption {
              type = types.port;
              default = 8501;
              description = "Port to listen on";
            };
            
            address = mkOption {
              type = types.str;
              default = "127.0.0.1";
              description = "Address to bind to";
            };
            
            openFirewall = mkOption {
              type = types.bool;
              default = false;
              description = "Whether to open the firewall port";
            };
          };
          
          config = mkIf cfg.enable {
            systemd.services.finplanner = {
              description = "Financial Planning Application";
              wantedBy = [ "multi-user.target" ];
              after = [ "network.target" ];
              
              environment = {
                HOME = "/tmp/finplanner-home";
                STREAMLIT_SERVER_HEADLESS = "true";
                STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false";
                STREAMLIT_CONFIG_DIR = "${self.packages.${pkgs.system}.finplanner}/share/finplanner/.streamlit";
              };
              
              serviceConfig = {
                ExecStartPre = "${pkgs.coreutils}/bin/mkdir -p /tmp/finplanner-home";
                ExecStart = "${self.packages.${pkgs.system}.finplanner}/bin/finplanner";
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
        
        pythonEnv = python.withPackages (ps: with ps; [
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
            
            # create directory structure
            mkdir -p $out/bin
            mkdir -p $out/share/finplanner
            mkdir -p $out/share/finplanner/.streamlit
            
            # copy application files
            cp -r *.py $out/share/finplanner/ 2>/dev/null || true
            cp -r static $out/share/finplanner/ 2>/dev/null || true
            cp -r assets $out/share/finplanner/ 2>/dev/null || true
            cp -r data $out/share/finplanner/ 2>/dev/null || true
            
            # copy streamlit config if it exists
            if [ -d ".streamlit" ]; then
              cp -r .streamlit/* $out/share/finplanner/.streamlit/
            fi
            if [ -f "config.toml" ]; then
              cp config.toml $out/share/finplanner/.streamlit/
            fi
            
            # create wrapper script using makeWrapper
            makeWrapper ${pythonEnv}/bin/streamlit $out/bin/finplanner \
              --add-flags "run" \
              --add-flags "$out/share/finplanner/app.py" \
              --add-flags "--server.port=8501" \
              --add-flags "--server.address=0.0.0.0" \
              --add-flags "--server.headless=true" \
              --add-flags "--browser.gatherUsageStats=false" \
              --add-flags "--theme.base=dark" \
              --add-flags "--theme.primaryColor=#81a1c1" \
              --add-flags "--theme.backgroundColor=#2e3440" \
              --add-flags "--theme.secondaryBackgroundColor=#3b4252" \
              --add-flags "--theme.textColor=#eceff4" \
              --set PYTHONPATH "$out/share/finplanner:${pythonEnv}/${pythonEnv.sitePackages}" \
              --set STREAMLIT_CONFIG_DIR "$out/share/finplanner/.streamlit" \
              --set-default HOME "/tmp" \
              --prefix PATH : ${pkgs.lib.makeBinPath [ 
                pkgs.coreutils 
                pkgs.findutils 
                pkgs.gnugrep 
                pkgs.gnused 
              ]}
            
            runHook postInstall
          '';
          
          meta = with pkgs.lib; {
            description = "Financial Planning Application";
            license = licenses.mit;
            platforms = platforms.unix;
            mainProgram = "finplanner";
          };
        };
        
      in {

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            python.pkgs.black
            python.pkgs.pylint
            python.pkgs.ipython
          ];
          
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
            
            # set environment variables for development
            export PYTHONPATH="$PWD:$PYTHONPATH"
            export STREAMLIT_CONFIG_DIR="$PWD/.streamlit"
            
            # ensure config directory exists
            mkdir -p .streamlit
            
            # create config.toml if it doesn't exist
            if [ ! -f .streamlit/config.toml ] && [ -f config.toml ]; then
              cp config.toml .streamlit/
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