{pkgs}: {
  deps = [
    pkgs.jq
    pkgs.postgresql
    pkgs.rustc
    pkgs.pkg-config
    pkgs.openssl
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cargo
  ];
}
