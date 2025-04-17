{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs =
    { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      lib = nixpkgs.lib;
      bpyDeps = with pkgs.xorg; [
        libICE
        libSM
        libX11
        libXfixes
        libXi
        libXrender
        libXxf86vm
        pkgs.libGL
        pkgs.libxkbcommon
        pkgs.libz
        pkgs.stdenv.cc.cc.lib
      ];
    in
    {
      packages.x86_64-linux.default = pkgs.mkShell {
        LD_LIBRARY_PATH = lib.makeLibraryPath bpyDeps;
        packages = with pkgs; [
          blender

          python311
          python311Packages.pip
          python311Packages.venvShellHook

          # Requirements for bpy
        ];
        venvDir = ".venv";
        postVenvCreation = ''
          unset SOURCE_DATE_EPOCH
          pip install -r requirements.txt
        '';
      };
    };
}
