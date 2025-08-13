(
    if [ -f "docling-dify-plugin.difypkg" ]; then
        rm docling-dify-plugin.difypkg
    fi
    cd ../;
    dify plugin package docling-dify-plugin/ \
        && mv docling-dify-plugin.difypkg docling-dify-plugin/
)