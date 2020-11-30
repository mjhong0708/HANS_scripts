!/usr/bin/bash
efermi=`grep efermi vasprun.xml | awk '{print $3}'`
echo $efermi
#if spin polarized
awk '/<total>/, /<\/total>/' vasprun.xml | awk '/spin 1/, /\/set>/ {print $2 - $efermi, $3}' | tail -n+2 | head -n-1 > tdos_up.dat
awk '/<total>/, /<\/total>/' vasprun.xml | awk '/spin 2/, /\/set>/ {print $2 - $efermi, $3}' | tail -n+2 | head -n-1 > tdos_down.dat

cat >plotfile<<!
set term x11 font "arial,15" size 1200,800
set xlab "E-E_F (eV)"
set ylab "DOS (arb. units)"

plot "tdos_up.dat" using (\$1-$efermi):(\$2) w l lt -1 t "up", \
     "tdos_down.dat" using (\$1-$efermi):(-\$2) w l lt 3 t "down"
!

gnuplot -persist plotfile
