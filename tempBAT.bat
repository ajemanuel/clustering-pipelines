title temp bat for clustering
pushd \\research.files.med.harvard.edu\Neurobio
cd HarveyLab\Alan\Data\20170622\p5_brush
klusta hindpaw.prm --overwrite
cd HarveyLab\Alan\Data\20170622\p7_brush
klusta forepaw.prm --overwrite
cd HarveyLab\Alan\Data\20170622\p2_brush
klusta brush.prm --overwrite
popd