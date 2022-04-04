doc = arguments[0]
destination = arguments[1]

function saveAndClose(doc, dest) {
    var saveName = new File(dest);
    saveOpts = new PDFSaveOptions();
    saveOpts.compatibility = PDFCompatibility.ACROBAT8;
    saveOpts.generateThumbnails = false;
    saveOpts.preserveEditability = false;
    doc.saveAs(saveName, saveOpts);
    doc.close();
}

saveAndClose(doc, destination)