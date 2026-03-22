{
  description = "Vish is a graphical editor for creating and managing Bash scripts using a node-based interface";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs, ... } @ inputs:
  let
    supportedSystems = [
      "aarch64-darwin"
      "aarch64-linux"
      "x86_64-darwin"
      "x86_64-linux"
    ];

    forAllSystems = (systems: perSystemFlake:
      builtins.foldl' (acc: system:
        let
          inputs' = {
            pkgs = nixpkgs.legacyPackages.${system};
          };

          systemWrapper = (attr: set: { ${system} = set; });
        in
        acc // (builtins.mapAttrs systemWrapper (perSystemFlake inputs'))
      ) {} systems
    );

    vish = (
      {
        makeWrapper,
        stdenv,
        lib,
        meson,
        ninja,
        python3,
        qt6,
      }:
      let
        python = python3.withPackages (python-pkgs: (with python-pkgs; [
          pyside6
          shiboken6
        ]));

      inherit (qt6)
        qtbase
        wrapQtAppsHook
        ;
      in
      stdenv.mkDerivation {
        pname = "vish";
        version = lib.fileContents ./VERSION;

        src = lib.fileset.toSource {
          root    = ./.;
          fileset = lib.fileset.gitTracked ./.;
        };

        buildInputs = [
          makeWrapper
          meson
          ninja
          python
          qtbase
        ];

        nativeBuildInputs = [
          wrapQtAppsHook
        ];

        postInstall = ''
          makeWrapper '${python}/bin/python3' "$out/bin/vish" \
            --prefix QT_PLUGIN_PATH : "${qtbase}/${qtbase.qtPluginPrefix}" \
            --add-flag "$out/share/vish/main.py"
        '';

        meta = {
          description = "Vish is a graphical editor for creating and managing Bash scripts using a node-based interface";
          homepage = "https://github.com/Lluciocc/Vish";
          license = lib.licenses.mit;
          sourceProvenance = with lib.sourceTypes; [ fromSource ];
          mainProgram = "vish";
          platforms = supportedSystems;
        };
      }
    );
  in
  {
    overlays.default = final: prev: {
      vish = self.packages.${prev.stdenv.hostPlatform.system}.vish;
    };
  } //
  forAllSystems supportedSystems (
    { pkgs, ... }:
    let
      package = pkgs.callPackage vish {};
      app = {
        type = "app";
        program = "${package}/bin/vish";
        inherit (package) meta;
      };
      shell = pkgs.mkShell {
        buildInputs = with pkgs; [
          python3Packages.virtualenv
          python3Packages.pyside6
          python3Packages.shiboken6
          qt6.qtbase
        ];
        shellHook = ''
          export QT_PLUGIN_PATH="${pkgs.qt6.qtbase}/${pkgs.qt6.qtbase.qtPluginPrefix}":$QT_PLUGIN_PATH
        '';
      };
    in
    {
      packages.vish    = package;
      packages.default = package;

      apps.vish     = app;
      apps.default  = app;

      devShells.default = shell;
    }
  );
}
