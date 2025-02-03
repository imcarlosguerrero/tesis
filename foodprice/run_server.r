# run_plumber.R
library(plumber)
# This will load your API from server.R and start it on port 4000.
pr("../foodprice/server.R") %>% pr_run(port = 4000)