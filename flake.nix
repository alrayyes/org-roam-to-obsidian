{
  description = "Convert org-roam notes to Obsidian markdown format";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        # nixos-unstable's python3 is already 3.14, matching this repo's own
        # `requires-python = ">=3.14"` — no override needed.
        python3 = pkgs.python3;
        # Kept in sync with pyproject.toml's [project].version by hand —
        # release-please owns that file, not this one.
        version = "3.7.3";
      in
      {
        packages.default = python3.pkgs.buildPythonApplication {
          pname = "org-roam-to-obsidian";
          inherit version;

          src = ./.;

          # convert.py is a single top-level script, not a package: no
          # [build-system] table in pyproject.toml and nothing outside the
          # standard library to depend on (see pyproject.toml's own pytest
          # comment on the same point). `format = "other"` skips the
          # pyproject build backend entirely; the install phase below is
          # the whole build.
          format = "other";
          dontBuild = true;

          installPhase = ''
            install -Dm755 convert.py $out/bin/org-roam-to-obsidian
          '';

          # The real coverage for convert.py's behavior is pytest, already
          # run in CI outside Nix; this build only proves the package
          # itself installs and runs.
          doCheck = false;

          meta = {
            description = "Convert org-roam notes to Obsidian markdown format";
            homepage = "https://github.com/alrayyes/org-roam-to-obsidian";
            license = pkgs.lib.licenses.gpl3Plus;
            mainProgram = "org-roam-to-obsidian";
          };
        };

        apps.default = flake-utils.lib.mkApp { drv = self.packages.${system}.default; };
      }
    );
}
