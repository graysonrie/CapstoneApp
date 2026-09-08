{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  packages = with pkgs; [
    cargo
    cargo-xwin
    rustc
    rustfmt
    rustPackages.clippy
    pre-commit
    nodejs
    pnpm
    pkg-config
    openssl
    mesa
    glib
    gtk3
    webkitgtk_4_1
    libsoup_3
    gdk-pixbuf
    pango
    atk
    cairo
    harfbuzz
    librsvg
    libayatana-appindicator
    linuxdeploy
    patchelf
  ];
  RUST_SRC_PATH = pkgs.rustPlatform.rustLibSrc;

  LIBGL_DRIVERS_PATH = "${pkgs.mesa}/lib/dri";
  __EGL_VENDOR_LIBRARY_FILENAMES = "${pkgs.mesa}/share/glvnd/egl_vendor.d/50_mesa.json";
}
