%global rust_triple x86_64-unknown-linux-gnu

Name:           cargo
Version:        0.32.0
Release:        30
Summary:        Rust package manager and build tool
License:        Apache-2.0 MIT
URL:            https://crates.io/
Source0:        https://github.com/rust-lang/cargo/archive/0.32.0/cargo-0.32.0.tar.gz
Source1:        http://localhost/cgit/projects/cargo-vendor/snapshot/cargo-vendor-0.32.0.tar.gz
Patch1:         0001-Fix-type-passed-to-Hasher.patch

BuildRequires:  cmake
BuildRequires:  curl
BuildRequires:  curl-dev
BuildRequires:  gcc
BuildRequires:  libgit2-dev
BuildRequires:  libssh2-dev
BuildRequires:  make
BuildRequires:  openssl-dev
BuildRequires:  pkg-config
BuildRequires:  python
BuildRequires:  rustc
BuildRequires:  zlib-dev
BuildRequires:  %{name} >= 0.17.0
Requires:       rustc

%description
Language package and dependency manager for Rust.


%prep

# vendored crates
%setup -q -n cargo-vendor-0.32.0 -T -b 1

# cargo sources
%setup -q

%patch1 -p1

# Create vendored dependencies for offline build see
# https://github.com/alexcrichton/cargo-vendor/
# Generated via checking out cargo version from git and running
# ver="" && cargo vendor && mv vendor cargo-vendor-$ver && tar cf cargo-vendor-$ver.tar cargo-vendor-$ver && gzip cargo-vendor-$ver.tar
# TODO: package these dependencies for the distribution
mkdir -p .cargo
cat >.cargo/config <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/../cargo-vendor-0.32.0'
EOF

%build

# use our offline registry
mkdir -p .cargo
export CARGO_HOME=$PWD/.cargo

%install
# convince libgit2-sys to use the distro libgit2
export LIBGIT2_SYS_USE_PKG_CONFIG=1
# Enable optimization, debuginfo, and link hardening.
export RUSTFLAGS="-C opt-level=3 -g -Clink-args=-Wl,-z,relro,-z,now"

cargo install --root %{buildroot}/usr --path .
install -p -m644 src/etc/_cargo -D %{buildroot}/usr/share/zsh/site-functions/_cargo
mkdir -p %{buildroot}/usr/share/man/man1
install -p -m644 src/etc/man/cargo*.1 -D %{buildroot}/usr/share/man/man1
install -p -m644 src/etc/cargo.bashcomp.sh -D %{buildroot}/usr/share/bash_completion.d/cargo
# Remove installer artifacts (manifests, uninstall scripts, etc.)
rm %{buildroot}/usr/.crates.toml

%files
/usr/bin/cargo
/usr/share/bash_completion.d/cargo
/usr/share/man/man1/cargo*.1
/usr/share/zsh/site-functions/_cargo
