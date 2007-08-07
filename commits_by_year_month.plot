set terminal png
set size 0.5,0.5
set output 'commits_by_year_month.png'
unset key
set xdata time
set timefmt "%Y-%m"
set format x "%Y-%m"
plot 'commits_by_year_month.dat' using 1:2 w lp
