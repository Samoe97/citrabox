doc = arguments[0]
destination = arguments[1]

function saveAndClose(doc, dest) {

    // app.open(dest)

    // app.doAction("Sample underprint white test 1", "To add White Underprint")

    var saveName = new File(dest);

    saveOpts = new PDFSaveOptions();
    saveOpts.preserveEditing = false;

    doc.saveAs(saveName, saveOpts);
    doc.close();

}

saveAndClose(doc, destination)