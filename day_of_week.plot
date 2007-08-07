set terminal png
set size 0.5,0.5
set output 'day_of_week.png'
unset key
set xrange [0.5:7.5]
plot 'day_of_week.dat' using 1:2:(0.5) w boxes fs solid
