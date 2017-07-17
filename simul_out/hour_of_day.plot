set terminal png transparent size 640,240
set size 1.0,1.0

set output 'hour_of_day.png'
unset key
set xrange [0.5:24.5]
set yrange [0:]
set xtics 4
set grid y
set ylabel "Commits"
plot 'hour_of_day.dat' using 1:2:(0.5) w boxes fs solid
