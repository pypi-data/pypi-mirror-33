document.write('\
<center>\
  <div align="center" valign="middle">\
  <ul class="icyLink">\
    <a href="population.html"><div class=menu-button> Population </div></a>\
    <a href="genome_structure.html" ><div class=menu-button> Genome structure </div></a>\
    <a href="genome_stats.html" ><div class=menu-button> Genome Stats </div></a>\
    <a href="cell.html" ><div class=menu-button> Inside the cell  </div></a>\
    <a href="grn.html"><div class=menu-button>  Gene regulatory network </div></a>\
    <a href="metabolism.html"> <div class=menu-button> Metabolism </div></a>\
    <a href="phylogeny.html"><div class=menu-button>  Phylogeny  </div></a>\
    <a href="species.html" ><div class=menu-button> Species  </div></a>\
    <a href="reactions.html" ><div class=menu-button> Reactions </div></a>\
    <a href="diversity.html" ><div class=menu-button> Diversity </div></a>\
    <a href="grid.html"><div class=menu-button>  Grid dynamics </div></a>\
    <a href="parameters.html"><div class=menu-button>  Parameters </div></a>\
    <br><center> <font size="1"><a href="../"> Browse simulation root </a> | <a href="../plots"> Browse plots </a> | <a href="../ancestry" title="Only works after LOD-analyses"> Browse ancestry </a> </font></center>\
  </div>\
  </ul>\
</center>\
\
');
var loc = window.location.pathname;
var filename = loc.substring(loc.lastIndexOf('/')+1);

$('.icylink').find('a').each(function() {
  $(this).toggleClass('active', $(this).attr('href') == filename);
});

function changeClass() {
    document.getElementById("menu-button-hover").className = "menu-button-hover";
}
