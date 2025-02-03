HCost <- function(Month = NULL, Year = NULL, City = NULL, Household, Data = NULL, ERR = NULL, EER_LL = NULL, UL = NULL, Serv = NULL, Diverse = NULL, exclude=NULL) {

  # Carga de librerías
  Librerias_base <- c("here", "readxl", "tidyverse", "knitr", "moments", "xgboost", "maditr",
                      "mice", "VIM", "dplyr", "finalfit", "plyr", "hdd", "zip", "httr",
                      "caret", "nnet", "quantreg", "gridExtra", "ggpubr", "cowplot")
  if (!require("pacman")) install.packages("pacman")
  pacman::p_load(char = Librerias_base, character.only = TRUE)

  #-------------------------------------------------#
  #  Validación de parámetros de la función         #
  #-------------------------------------------------#
  suppress_all <- function(expr) {
    sink(tempfile()) # Redirige la salida a un archivo temporal
    on.exit(sink())  # Asegura que la salida se restablezca al salir de la función

    invisible(capture.output({
      suppressMessages(suppressWarnings({
        result <- expr
      }))
    }))

    return(result)
  }


  # Validar tipo y estructura del dataframe Household
  validar_household_type <- function(household_type) {
    if (!is.data.frame(household_type)) {
      stop("Household debe ser un dataframe.")
    }

    if (ncol(household_type) != 3) {
      stop("Household debe tener exactamente 3 columnas.")
    }

    if (!all(c("Person", "Sex", "Demo_Group") %in% colnames(household_type))) {
      stop("Household debe tener las columnas Person, Sex y Demo_Group.")
    }

    if (!all(sapply(household_type$Person, is.numeric))) {
      stop("La columna Person de Household debe ser numérica.")
    }

    if (!all(household_type$Sex %in% c(0, 1))) {
      stop("La columna Sex de Household debe contener solo valores 0 o 1.")
    }

    if (!all(sapply(household_type$Demo_Group, is.character))) {
      stop("La columna Demo_Group de Household debe contener solo texto.")
    }
  }

  validar_household_type(Household)

  # Función para validar parámetros
  validar_parametros <- function(parametro, tipo, rango = NULL) {
    if (missing(parametro)) {
      stop("Parámetro faltante: ", deparse(substitute(parametro)))
    }

    tipo_funcion <- switch(tipo,
                           "numeric" = is.numeric,
                           "character" = is.character,
                           "list" = is.list,
                           "vector" = function(x) is.vector(x) || is.data.frame(x),
                           "default" = function(x) FALSE)

    if (!tipo_funcion(parametro)) {
      stop(paste("El parámetro", deparse(substitute(parametro)), "debe ser de tipo", tipo))
    }

    if (!is.null(rango) && !is.infinite(rango[1]) && !is.infinite(rango[2])) {
      if (parametro < rango[1] || parametro > rango[2]) {
        stop(paste("El parámetro", deparse(substitute(parametro)), "debe estar en el rango", rango[1], "-", rango[2]))
      }
    }
  }

  # Validar parámetros de entrada Month, Year y City si Data es NULL
  if (is.null(Data)) {
    validar_parametros(Month, "numeric", c(1, 12))
    validar_parametros(Year, "numeric", c(2022, 2023))
    validar_parametros(City, "character")

    cat("\n Se utilizará la función DataCol del paquete FoodpriceR para estimaciones.\n")
    Data_mes_año <- suppress_all(FoodpriceR::DataCol(Month = Month, Year = Year, City = City))

  } else if (!is.null(exclude)) {
    # Validar si exclude es un vector
    if (!is.vector(exclude)) {
      stop("The 'exclude' parameter must be a vector.")
    }

    # Filtrar los alimentos que no están en exclude
    Data_mes_año <- Data[!(Data$Food %in% exclude), ]
  } else {
    Data_mes_año <- Data
  }


  # Ejecutar modelo CoCA si ERR no es NULL
  if (!is.null(ERR)) {
    cat(" Ejecutando modelo CoCA. \n")
    modelo_1 <- suppress_all(FoodpriceR::CoCA(data = Data_mes_año, EER = ERR)$cost)

    model_dieta_1 <- merge(Household, modelo_1[c("Demo_Group", "Sex", "cost_day")],
                           by = c("Demo_Group", "Sex"),
                           all.x = TRUE, all.y = FALSE)
    model_dieta_1$hogar_total <- sum(as.numeric(model_dieta_1$cost_day))
    model_dieta_1$per_capita <- model_dieta_1$hogar_total / nrow(model_dieta_1)
    model_dieta_1$per_capita_year <- model_dieta_1$per_capita * 365
    model_dieta_1$per_capita_month <- model_dieta_1$per_capita * 30
  } else {
    cat("No se ejecutará la parte correspondiente al modelo CoCA porque ERR es NULL.\n")
    model_dieta_1 <- NULL
  }

  # Ejecutar modelo CoNA si EER_LL y UL no son NULL
  if (!is.null(EER_LL) && !is.null(UL)) {

    cat(" Ejecutando modelo CoNA.\n")

    # Uso de la función
    modelo_2 <- suppress_all(FoodpriceR::CoNA(data = Data_mes_año, EER_LL = EER_LL, UL = UL)$cost)

    model_dieta_2 <- merge(Household, modelo_2[c("Demo_Group", "Sex", "cost_day")],
                           by = c("Demo_Group", "Sex"),
                           all.x = TRUE, all.y = FALSE)
    model_dieta_2$hogar_total <- sum(as.numeric(model_dieta_2$cost_day))
    model_dieta_2$per_capita <- model_dieta_2$hogar_total / nrow(model_dieta_2)
    model_dieta_2$per_capita_year <- model_dieta_2$per_capita * 365
    model_dieta_2$per_capita_month <- model_dieta_2$per_capita * 30
  } else {
    cat("No se ejecutará la parte correspondiente al modelo CoNA porque EER_LL y/o UL son NULL.\n")
    model_dieta_2 <- NULL
  }

  # Ejecutar modelo CoRD si Serv y Diverse no son NULL
  if (!is.null(Serv) && !is.null(Diverse)) {

    cat(" Ejecutando modelo CoRD.\n")


    modelo_3 <- suppress_all(FoodpriceR::CoRD(data = Data_mes_año, diverse = Diverse, serv = Serv)$cost)

    model_dieta_3 <- merge(Household, modelo_3[c("Demo_Group", "Sex", "cost_day")],
                           by = c("Demo_Group", "Sex"),
                           all.x = TRUE, all.y = FALSE)
    model_dieta_3$hogar_total <- sum(as.numeric(model_dieta_3$cost_day))
    model_dieta_3$per_capita <- model_dieta_3$hogar_total / nrow(model_dieta_3)
    model_dieta_3$per_capita_year <- model_dieta_3$per_capita * 365
    model_dieta_3$per_capita_month <- model_dieta_3$per_capita * 30
  } else {
    cat("No se ejecutará la parte correspondiente al modelo CoRD porque Serv y/o Diverse son NULL.\n")
    model_dieta_3 <- NULL
  }

  # Cambiar nombres de columnas
  new_names_model_dieta <- c(
    "Demo_Group",
    "Sex",
    "Person",
    "cost_day",
    "total_household",
    "per_capita",
    "per_capita_year",
    "per_capita_month"
  )

  # Asignar nombres a los modelos y eliminar NULL
  resultado <- list(Model_CoCA = model_dieta_1, Model_CoNA = model_dieta_2, Model_CoRD = model_dieta_3)
  resultado <- resultado[!sapply(resultado, is.null)]  # Eliminar modelos NULL

  # Cambiar nombres de columnas
  for (i in seq_along(resultado)) {
    names(resultado[[i]]) <- new_names_model_dieta
  }

  cat("Proceso completado.\n")

  return(resultado)
}









