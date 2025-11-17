{
  description = "Financial planning application";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        python-deps = with pkgs.python3Packages; [
          streamlit
          numpy
          pandas
          matplotlib
          scipy
        ];
        
        finplanner = pkgs.python3Packages.buildPythonApplication {
          pname = "finplanner";
          version = "1.0.0";
          src = ./.;
          
          propagatedBuildInputs = python-deps;
          
          doCheck = false;
          
          installPhase = ''
            mkdir -p $out/bin $out/share/finplanner
            cp -r . $out/share/finplanner/
            
            cat > $out/bin/finplanner << EOF
            #!/bin/sh
            cd $out/share/finplanner
            ${pkgs.python3}/bin/python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 "\$@"
            EOF
            chmod +x $out/bin/finplanner
          '';
        };
        
      in {
        # development shell
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python3
          ] ++ python-deps ++ [
            python3Packages.jupyter
            python3Packages.ipython
          ];
          
          shellHook = ''
            echo ""
            echo "Financial Modeling environment activated"
            echo "  streamlit run app.py   - Launch web app"
            echo ""
          '';
        };
        
        # package for deployment
        packages.default = finplanner;
        packages.finplanner = finplanner;
        
        # nixos service module
        nixosModules.default = { config, lib, pkgs, ... }: {
          options.services.finplanner = {
            enable = lib.mkEnableOption "Financial planning application";
            port = lib.mkOption {
              type = lib.types.int;
              default = 8501;
              description = "Port to listen on";
            };
            address = lib.mkOption {
              type = lib.types.str;
              default = "127.0.0.1";
              description = "Address to bind to";
            };
          };
          
          config = lib.mkIf config.services.finplanner.enable {
            systemd.services.finplanner = {
              description = "Financial Planning Application";
              wantedBy = [ "multi-user.target" ];
              after = [ "network.target" ];
              
              serviceConfig = {
                ExecStart = "${finplanner}/bin/finplanner --server.port=${toString config.services.finplanner.port} --server.address=${config.services.finplanner.address}";
                Restart = "always";
                RestartSec = "10";
                User = "finplanner";
                Group = "finplanner";
                DynamicUser = true;
              };
            };
            
            networking.firewall.allowedTCPPorts = lib.mkIf (config.services.finplanner.address == "0.0.0.0") [ config.services.finplanner.port ];
          };
        };
      }
    );
}
