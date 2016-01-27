g = new Dygraph(
  document.getElementById("graph"),
    data,
      {
        labels: [ "Turn", "Similarity"],
        ylabel: 'Similarity',
        xlabel: 'Turn Number',
        digitsAfterDecimal: 5
    }     
);

// display the conversation
document.getElementById("annotation").innerHTML = buildAnnotation(tbt);

function buildAnnotation(tbtConv){
    var text = "<div class='annotation'>";

    for (var index =0; index < tbtConv.length; index++) {
        text += '<span onmouseover="mouseover(this)" onmouseout="mouseout(this)"id='+(index+1)+'>' + tbtConv[index] + "</span><br />";
    }
    text += "</div>";

    return text;
}
function mouseover (x) {
    highlight(x.id, true);
    g.setSelection(x.id);
}
function mouseout (x) {
    unhighlight();
    g.clearSelection();
}
function unhighlight () {
    for (var index=1; index <= tbt.length; index++ ){
        document.getElementById(index).removeAttribute("class");
    }
}
function highlight (x, mouseover) {
    var target;
    mouseover = mouseover || false;
    if (x > 0){
        if (x==1){
            highlightTurn(1);
            if (!mouseover){   
                target = document.getElementById(1);
                target.parentNode.scrollTop = target.offsetTop;
            }
        }else if (x==2) {
            highlightTurn(2);
            highlightWindow(1);
            if(!mouseover){
                target = document.getElementById(1);
                target.parentNode.scrollTop = target.offsetTop;
            }
        }else if (x==3) {
            highlightTurn(3);
            highlightWindow(2);
            highlightWindow(1);
            if(!mouseover){
                target = document.getElementById(1);
                target.parentNode.scrollTop = target.offsetTop;
            }
        }else {
            highlightTurn(x);
            highlightWindow(x-1);
            highlightWindow(x-2);
            highlightWindow(x-3);
            if(!mouseover){
                target = document.getElementById(x-3);
                target.parentNode.scrollTop = target.offsetTop;
            }
        }
    }
}
function highlightTurn (x) {
    document.getElementById(x).className = "turn-highlight";
}
function highlightWindow (x) {
    document.getElementById(x).className = "window-highlight";
}
g.updateOptions( {
    highlightCallback: function(event, x, points, row, seriesName) {
        unhighlight();
        highlight(x);
    },
    unhighlightCallback: function(event) {
        unhighlight(); 
    }
});