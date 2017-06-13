set terminal png transparent size 640,240
set size 1.0,1.0

set output 'month_of_year.png'
unset key
set xrange [0.5:12.5]
set yrange [0:]
set xtics 1
set grid y
set ylabel "Commits"
plot 'month_of_year.dat' using 1:2:(0.5) w boxes fs solid
