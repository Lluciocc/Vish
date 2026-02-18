project(
  'vish',
  version: '1.0.6',
  meson_version: '>=0.56'
)
python = import('python').find_installation('python3')
install_subdir(
  '.',
  install_dir: get_option('datadir') / 'vish',
  exclude_directories: ['.git', 'flatpak', 'data', '.github']
)
configure_file(
   input: 'vish.in',
  output: 'vish',
  copy: true,
  install: true,
  install_dir: get_option('bindir')
)
install_data(
  'data/io.github.lluciocc.Vish.desktop',
   install_dir: get_option('datadir') / 'applications'
)
install_data(
  'data/io.github.lluciocc.Vish.metainfo.xml',
  install_dir: get_option('datadir') / 'metainfo'
)
install_data(
   'data/io.github.lluciocc.Vish.png',
  install_dir: get_option('datadir') / 'icons/hicolor/256x256/apps'
)
