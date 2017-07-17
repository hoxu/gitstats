set terminal png transparent size 640,240
set size 1.0,1.0

set output 'files_by_date.png'
unset key
set yrange [0:]
set xdata time
set timefmt "%Y-%m-%d"
set format x "%Y-%m-%d"
set grid y
set ylabel "Files"
set xtics rotate
set ytics autofreq
set bmargin 6
plot 'files_by_date.dat' using 1:2 w steps
