{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShell = with pkgs; mkShell {
          buildInputs = [
            cargo
            cargo-xwin
            rustc
            rustfmt
            rustup
            pre-commit
            rustPackages.clippy
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
          RUST_SRC_PATH = rustPlatform.rustLibSrc;
          WEBKIT_DISABLE_DMABUF_RENDERER = "1";
          WEBKIT_DISABLE_COMPOSITING_MODE = "1";
          LIBGL_ALWAYS_SOFTWARE = "1";
          LIBGL_DRIVERS_PATH = "${mesa}/lib/dri";
          __EGL_VENDOR_LIBRARY_FILENAMES = "${mesa}/share/glvnd/egl_vendor.d/50_mesa.json";
        };
      }
    );
}
