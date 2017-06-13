set terminal png transparent size 640,240
set size 1.0,1.0

set output 'commits_by_year_month.png'
unset key
set yrange [0:]
set xdata time
set timefmt "%Y-%m"
set format x "%Y-%m"
set xtics rotate
set bmargin 5
set grid y
set ylabel "Commits"
plot 'commits_by_year_month.dat' using 1:2:(0.5) w boxes fs solid
