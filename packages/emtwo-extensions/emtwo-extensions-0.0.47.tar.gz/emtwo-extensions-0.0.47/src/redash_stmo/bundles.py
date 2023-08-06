from pywebpack import WebpackBundle
js = WebpackBundle(
    "./src/redash_stmo/js/datasource_link",
    entry={
        'datasource_link': './somefile.js',
    },
)