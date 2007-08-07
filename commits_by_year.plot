set terminal png
set size 0.5,0.5
set output 'commits_by_year.png'
unset key
plot 'commits_by_year.dat' using 1:2 w lp
