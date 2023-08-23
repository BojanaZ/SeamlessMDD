function load_tree() {
    console.log("Pozvano");
    $("#tree-view-from-json").jstree({
        core: {
            /**
             * Add the JSON content inside the "data" attribute.
             */
            data: [
                {
                    text: "JSON Node 1",
                    state: {
                        opened: true,
                    },
                    children: [
                        {
                            text: "JSON Node 1.1",
                        },
                        {
                            text: "JSON Node 1.2",
                        },
                        {
                            text: "JSON Node 1.3",
                        },
                        {
                            text: "JSON Node 1.4",
                        },
                        {
                            text: "JSON Node 1.5",
                        },
                    ],
                },
                {
                    text: "JSON Node 2",
                    state: {
                        opened: true,
                    },
                    children: [
                        {
                            text: "JSON Node 2.1",
                        },
                        {
                            text: "JSON Node 2.2",
                        },
                        {
                            text: "JSON Node 2.3",
                        },
                        {
                            text: "JSON Node 2.4",
                        },
                        {
                            text: "JSON Node 2.5",
                        },
                    ],
                },
            ],
        },
    });
}

//function createTree(data) {
//    const nodeWithParent = []
//
//    data.forEach(d => {
//        const parent = d.order.includes('.')?d.order.substr(0, d.order.lastIndexOf('.')):null
//        nodeWithParent.push({...d, parent})
//    })
//
//    function getNodeHtml(n) {
//        const children = nodeWithParent.filter(d => d.parent._id === n._id)
//        let html = '<li>' + n._name
//        if(children.length>0) {
//          html += '<ul>'
//            + children.map(getNodeHtml).join('')
//            + '</ul>'
//        }
//        html += '</li>'
//        return html
//    }
//}