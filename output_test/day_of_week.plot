set terminal png transparent size 640,240
set size 1.0,1.0

set output 'day_of_week.png'
unset key
set xrange [0.5:7.5]
set yrange [0:]
set xtics 1
set grid y
set ylabel "Commits"
plot 'day_of_week.dat' using 1:3:(0.5):xtic(2) w boxes fs solid
