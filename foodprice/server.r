# server.r

library(FoodpriceR)

data_files <- list.files("data", pattern = "\\.(csv|rda|RData)$", full.names = TRUE)
for (file in data_files) {
  if (grepl("\\.csv$", file, ignore.case = TRUE)) {
    # Use the file name (without extension) as the variable name.
    data_name <- tools::file_path_sans_ext(basename(file))
    assign(data_name, read.csv(file), envir = .GlobalEnv)
  } else {
    # For RData files, load them (this will load any objects stored in the file)
    load(file, envir = .GlobalEnv)
  }
}

get_model <- function(model_func, data, ...) {
  exclude_list <- strsplit(...$exclude, ",\\s*")[[1]]
  Modelo <- model_func(data = data, exclude = exclude_list, ...)
  return(Modelo)
}

#* Returns a CoCA
#* @param exclude Foods to be excluded from the CoCA
#* @get /api/r/get_coca
function(exclude = "") {
  exclude_list <- strsplit(exclude, ",\\s*")[[1]]
  Modelo = FoodpriceR::CoCA(data = scraped_dataframe, EER = EER, exclude = exclude_list)
  return(Modelo)
}

#* Returns a CoNA
#* @param exclude Foods to be excluded from the CoNA
#* @get /api/r/get_cona
function(exclude = "") {
  exclude_list <- strsplit(exclude, ",\\s*")[[1]]
  Modelo = FoodpriceR::CoNA(data = scraped_dataframe, EER_LL = EER_LL, UL = UL, exclude = exclude_list)
  return(Modelo)
}

#* Returns a CoRD
#* @param exclude Foods to be excluded from the CoRD
#* @get /api/r/get_cord
function(exclude = "") {
  exclude_list <- strsplit(exclude, ",\\s*")[[1]]
  Modelo = FoodpriceR::CoRD(data = scraped_dataframe, serv = serv2, diverse = diverse, exclude = exclude_list)
  return(Modelo)
}