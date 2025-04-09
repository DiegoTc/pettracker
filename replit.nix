{pkgs}: {
  deps = [
    pkgs.mosquitto
    pkgs.jq
    pkgs.postgresql
    pkgs.openssl
  ];
}
