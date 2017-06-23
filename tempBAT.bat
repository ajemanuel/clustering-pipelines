@echo off
title temp bat for clustering
pushd \\research.files.med.harvard.edu\Neurobio
cd HarveyLab\Alan\Data\20170622\p3_brush
klusta forepaw.prm
cd HarveyLab\Alan\Data\20170622\p5_brush
klusta hindpaw.prm
cd HarveyLab\Alan\Data\20170622\p7_brush
klusta forepaw.prm
popd
exit
