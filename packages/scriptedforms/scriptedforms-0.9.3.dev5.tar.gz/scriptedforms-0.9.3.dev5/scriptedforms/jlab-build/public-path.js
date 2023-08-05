var CONFIG_DIV = document.getElementById('scriptedforms-config-data');
if (CONFIG_DIV) {
    var config = JSON.parse(CONFIG_DIV.textContent);
    __webpack_public_path__ = config.publicPath;
}
//# sourceMappingURL=public-path.js.map