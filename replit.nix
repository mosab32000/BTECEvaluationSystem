{pkgs}: {
  deps = [
    pkgs.lsof
    pkgs.postgresql
    pkgs.rustc
    pkgs.pkg-config
    pkgs.openssl
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cargo
  ];
}
