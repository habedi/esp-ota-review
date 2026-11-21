{
  description = "The development environment for Zaptec's technical case";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            packages = with pkgs; [
              git cmake ninja gnumake uv python315 pkg-config
              (texlive.withPackages (ps: [
                ps.scheme-small ps.lm ps.fira ps.fontaxes ps.mweights
                ps.beamertheme-metropolis ps.pgfopts ps.listings
              ]))
            ];
            shellHook = pkgs.lib.optionalString pkgs.stdenv.hostPlatform.isLinux ''
              export LD_LIBRARY_PATH="${pkgs.libslirp}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
              export LOCALE_ARCHIVE="${pkgs.glibcLocales}/lib/locale/locale-archive"
            '';
          };
        }
      );
    };
}
