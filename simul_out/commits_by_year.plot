set terminal png transparent size 640,240
set size 1.0,1.0

set output 'commits_by_year.png'
unset key
set yrange [0:]
set xtics 1 rotate
set grid y
set ylabel "Commits"
set yrange [0:]
plot 'commits_by_year.dat' using 1:2:(0.5) w boxes fs solid
