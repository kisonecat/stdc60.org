{
  description = "stdc60.org — 60th Spring Topology and Dynamics Conference";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        hpkgs = pkgs.haskell.packages.ghc96;

        site = hpkgs.callCabal2nix "stdc60-org" ./. { };
      in
      {
        # The site executable itself
        packages.default = site;

        # `nix run` → site build
        apps.default = {
          type = "app";
          program = "${site}/bin/site";
        };

        # `nix run .#watch` → live-reload dev server
        apps.watch = {
          type = "app";
          program = toString (pkgs.writeShellScript "site-watch" ''
            exec ${site}/bin/site watch
          '');
        };

        devShells.default = hpkgs.shellFor {
          packages = _: [ site ];
          buildInputs = [
            hpkgs.cabal-install
            hpkgs.haskell-language-server
            hpkgs.ghcid
            pkgs.zlib
          ];
          withHoogle = true;
        };
      });
}
