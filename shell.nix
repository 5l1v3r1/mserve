with import <nixpkgs> {};

let

  mb = python3Packages.buildPythonPackage rec {
    name = "musicbrainzngs-0.6";
    src = pkgs.fetchurl {
      url = "mirror://pypi/m/musicbrainzngs/${name}.tar.gz";
      sha256 = "1dddarpjawryll2wss65xq3v9q8ln8dan7984l5dxzqx88d2dvr8";
    };
    buildInputs = [ pkgs.glibcLocales ];
    LC_ALL="en_US.UTF-8";
  };

in stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    python3
    python3Packages.mutagen
    python3Packages.flask
    mb
  ];
  shellHook = "export PYTHONPATH=.:$PYTHONPATH";
}
