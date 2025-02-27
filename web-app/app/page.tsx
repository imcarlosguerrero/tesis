"use client";

import { Button } from "@/components/ui/button";
import {
	Combobox,
	ComboboxAnchor,
	ComboboxBadgeItem,
	ComboboxBadgeList,
	ComboboxContent,
	ComboboxEmpty,
	ComboboxInput,
	ComboboxItem,
	ComboboxLabel,
	ComboboxTrigger,
} from "@/components/ui/combobox";
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { ThemeModeToggle } from "@/components/ui/theme-mode-toggle";
import {
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectLabel,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";

import axios from "axios";
import { ChevronDown } from "lucide-react";
import Image from "next/image";
import { useEffect, useState } from "react";
import * as React from "react";
import { set, useForm } from "react-hook-form";
// Add this
import { z } from "zod";

// Add this

import { zodResolver } from "@hookform/resolvers/zod";

const tricks = [
	{ label: "Kickflip", value: "kickflip" },
	{ label: "Heelflip", value: "heelflip" },
	{ label: "Tre Flip", value: "tre-flip" },
	{ label: "FS 540", value: "fs-540" },
	{ label: "Casper flip 360 flip", value: "casper-flip-360-flip" },
	{ label: "Kickflip Backflip", value: "kickflip-backflip" },
	{ label: "360 Varial McTwist", value: "360-varial-mc-twist" },
	{ label: "The 900", value: "the-900" },
];

const formSchema = z.object({
	nombre: z.string().nonempty("Requerido"),
	dieta: z.enum(["Dieta de subsistencia", "Dieta suficiente en nutrientes", "Dieta saludable"]),
	edad: z.preprocess(
		(val) => Number(val),
		z.number({ required_error: "Requerido" }).min(1, "La edad debe ser un número positivo mayor que 0")
	),
	sexo: z.enum(["Masculino", "Femenino"]),
	estadoEmbarazo: z.enum(["No aplica", "Gestante", "Lactante"]).optional(),
	delete: z.array(z.string()).optional(), // Added
});

type FormSchema = z.infer<typeof formSchema>;

export default function Home() {
	const [value, setValue] = React.useState<string[]>([]);
	const [loading, setLoading] = useState(false);
	const [isDialogOpen, setIsDialogOpen] = useState(false);
	const [responseData, setResponseData] = useState(null);
	const [tipoDieta, setTipoDieta] = useState("Dieta de subsistencia");
	const [costoDieta, setCostoDieta] = useState(0);
	const [nombre, setNombre] = useState("");
	const [alimentos, setAlimentos] = useState([]);

	useEffect(() => {
		(async () => {
			const res = await axios.get("/api/get_products");
			setAlimentos(res.data);
		})();
	}, []);

	useEffect(() => {
		if (alimentos.length > 0) {
			console.log(alimentos);
		}
	}, [alimentos]);

	const form = useForm<FormSchema>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			nombre: "",
			dieta: "Dieta de subsistencia",
			edad: 0,
			sexo: "Masculino",
			estadoEmbarazo: "No aplica",
		},
	});

	const sexoValue = form.watch("sexo");

	useEffect(() => {
		if (responseData) {
			if (tipoDieta === "Dieta de subsistencia") {
				setCostoDieta(parseFloat((responseData as CoCA).cost_day.toFixed(2)));
			} else {
				setCostoDieta(parseFloat(((responseData as CoNA).cost[0].cost_day).toFixed(2)));
			}
		}
	}, [responseData]);

	const onSubmit = async (values: FormSchema) => {
		setNombre(values.nombre);
		console.log("Delete elements:", values.delete);
		setLoading(true);

		try {
			console.log(values);
			let sex = 1;
			if (values.sexo === "Masculino") {
				sex = 0;
			}

			// Prepare exclude parameter if delete array has elements
			const excludeParam = values?.delete?.length > 0 ? `&exclude=${values?.delete.join(",")}` : "";

			// Prepare pregnancy/lactating parameter
			let pregnancyParam = "";
			if (values.sexo === "Femenino" && values.estadoEmbarazo) {
				if (values.estadoEmbarazo === "Gestante") {
					pregnancyParam = "&pregnant=True";
				} else if (values.estadoEmbarazo === "Lactante") {
					pregnancyParam = "&lactating=True";
				}
			}

			if (values.dieta === "Dieta de subsistencia") {
				setTipoDieta("Dieta de subsistencia");
				const res = await axios.get(
					`/api/get_coca?age=${values.edad}&sex=${sex}${excludeParam}${pregnancyParam}`
				);
				setResponseData(res.data);
			} else if (values.dieta === "Dieta suficiente en nutrientes") {
				setTipoDieta("Dieta suficiente en nutrientes");
				const res = await axios.get(
					`/api/get_cona?age=${values.edad}&sex=${sex}${excludeParam}${pregnancyParam}`
				);
				setResponseData(res.data);
			} else if (values.dieta === "Dieta saludable") {
				setTipoDieta("Dieta saludable");
				const res = await axios.get(
					`/api/get_cord?age=${values.edad}&sex=${sex}${excludeParam}${pregnancyParam}`
				);
				setResponseData(res.data);
			}
		} catch (error) {
			console.error(error);
		} finally {
			setLoading(false);
			setIsDialogOpen(true);
		}
	};

	return (
		
		<div className="flex flex-col items-center justify-center overflow-y-auto py-16">
			<div className="hidden">
			<ThemeModeToggle/>	
			</div>
			<section className="w-full max-w-4xl mb-12">
				<h2 className="text-lg lg:text-xl font-semibold text-gray-800 mb-6 text-center">
					Bienvenido a la calculadora de dietas
				</h2>
				<div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-[80%] md:[100%] mx-auto">
					<div className="bg-white p-6 rounded-lg shadow">
						<h3 className="text-md font-bold mb-2">1. Introduzca su nombre.</h3>
						<p className="text-gray-600">Esto nos permitirá generar una dieta con su nombre.</p>
					</div>
					<div className="bg-white p-6 rounded-lg shadow">
						<h3 className="text-md font-bold mb-2">2. Seleccione el tipo de dieta.</h3>
						<p className="text-gray-600">
							Con base en esto escogeremos una serie de alimentos que suplirán ciertas necesidades nutricionales diarias.
						</p>
					</div>
					<div className="bg-white p-6 rounded-lg shadow">
						<h3 className="text-md font-bold mb-2">3. Introduzca su edad.</h3>
						<p className="text-gray-600">
							Esto nos permitirá determinar sus requerimientos nutricionales diarios estimados.
						</p>
					</div>
					<div className="bg-white p-6 rounded-lg shadow">
						<h3 className="text-md font-bold mb-2">4. Introduzca su sexo.</h3>
						<p className="text-gray-600">
							Esto nos permitirá determinar sus requerimientos nutricionales diarios estimados.
						</p>
					</div>
					<div className="bg-white p-6 rounded-lg shadow">
						<h3 className="text-md font-bold mb-2">5. Introduzca su estado de embarazo.</h3>
						<p className="text-gray-600">
							Este paso solo es necesario si seleccionó "Femenino" en el paso anterior.
						</p>
					</div>
					<div className="bg-white p-6 rounded-lg shadow">
						<h3 className="text-md font-bold mb-2">6. Seleccione alimentos a eliminar.</h3>
						<p className="text-gray-600">
							Seleccione los alimentos que desea remover la dieta a generar, si no desea remover ninguno, deje este campo vacío.
						</p>
					</div>
					<div className="bg-white p-6 rounded-lg shadow">
						<h3 className="text-md font-bold mb-2">7. Genere su dieta.</h3>
						<p className="text-gray-600">
							Recuerde que los valores proporcionados son estimados y pueden variar de acuerdo con
							múltiples factores, también tenga en cuenta que esta calculadora provee de ingredientes, más no de recetas.
						</p>
					</div>
					<div className="bg-white p-6 rounded-lg shadow">
						<h3 className="text-md font-bold mb-2">8. Aclaración.</h3>
						<p className="text-gray-600">
							Las dietas generadas son estimaciones basadas en múltiples factores, por lo que se deben tratar como una guía y no como una dieta definitiva, por favor consulte a un profesional de la salud antes de realizar cambios en su dieta.
						</p>
					</div>
				</div>
			</section>
			<Form {...form}>
				<form
					onSubmit={form.handleSubmit(onSubmit)}
					className="w-[80%] sm:w-[70%] md:w-[60%] lg:w-[50%] xl:w-[40%] 2xl:w-[30%] flex flex-col gap-6"
				>
					<FormField
						control={form.control}
						name="nombre"
						render={({ field }) => (
							<FormItem>
								<FormLabel className="text-md font-bold">Introduzca su nombre</FormLabel>
								<FormControl>
									<Input className="text-sm" type="text" {...field} />
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>
					<FormField
						control={form.control}
						name="dieta"
						render={({ field }) => (
							<FormItem>
								<FormLabel className="text-md font-bold">Seleccione el tipo de dieta</FormLabel>
								<Select onValueChange={field.onChange} value={field.value}>
									<SelectTrigger className="text-sm">
										<SelectValue placeholder="Seleccione" />
									</SelectTrigger>
									<SelectContent>
										<SelectItem className="text-sm" value="Dieta de subsistencia">
											Dieta de subsistencia
										</SelectItem>
										<SelectItem className="text-sm" value="Dieta suficiente en nutrientes">
											Dieta suficiente en nutrientes
										</SelectItem>
										<SelectItem className="text-sm" value="Dieta saludable">
											Dieta saludable
										</SelectItem>
									</SelectContent>
								</Select>
								<FormMessage />
							</FormItem>
						)}
					/>
					<FormField
						control={form.control}
						name="edad"
						rules={{ min: { value: 1, message: "La edad debe ser mayor que 0" } }}
						render={({ field }) => (
							<FormItem>
								<FormLabel className="text-md font-bold">Introduzca su edad</FormLabel>
								<FormControl>
									<Input className="text-sm" type="number" min="1" {...field} />
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>
					<FormField
						control={form.control}
						name="sexo"
						render={({ field }) => (
							<FormItem>
								<FormLabel className="text-md font-bold">Sexo</FormLabel>
								<Select
									onValueChange={(value) => {
										field.onChange(value);
										if (value !== "Femenino") {
											form.setValue("estadoEmbarazo", "No aplica");
										}
									}}
									value={field.value}
								>
									<SelectTrigger>
										<SelectValue placeholder="Seleccione" />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="Masculino">Masculino</SelectItem>
										<SelectItem value="Femenino">Femenino</SelectItem>
									</SelectContent>
								</Select>
								<FormMessage />
							</FormItem>
						)}
					/>
					<FormField
						control={form.control}
						name="delete"
						render={({ field }) => (
							<FormItem>
								<FormLabel className="text-md font-bold">Eliminar alimentos</FormLabel>
								<Combobox
									value={field.value || []}
									onValueChange={(newValue) => field.onChange(newValue)}
									multiple
								>
									<ComboboxAnchor className="h-full min-h-10 flex-wrap px-3 py-2">
										<ComboboxBadgeList>
											{(field.value || []).map((item) => {
												const option = alimentos.find((alimento) => alimento.name === item);
												if (!option) return null;

												return (
													<ComboboxBadgeItem key={item} value={item}>
														{option.name}
													</ComboboxBadgeItem>
												);
											})}
										</ComboboxBadgeList>
										<ComboboxInput
											placeholder="Eliminar alimentos..."
											className="h-auto min-w-20 flex-1"
										/>
										<ComboboxTrigger className="absolute top-3 right-2">
											<ChevronDown className="h-4 w-4" />
										</ComboboxTrigger>
									</ComboboxAnchor>
									<ComboboxContent className="relative max-h-[300px] overflow-y-auto overflow-x-hidden">
										{alimentos.map((alimento) => (
											<ComboboxItem key={alimento.name} value={alimento.name}>
												{alimento.name}
											</ComboboxItem>
										))}
									</ComboboxContent>
								</Combobox>
								<FormMessage />
							</FormItem>
						)}
					/>
					{sexoValue === "Femenino" && (
						<FormField
							control={form.control}
							name="estadoEmbarazo"
							render={({ field }) => (
								<FormItem>
									<FormLabel className="text-md font-bold">Estado de Embarazo</FormLabel>
									<Select onValueChange={field.onChange} value={field.value}>
										<SelectTrigger>
											<SelectValue placeholder="Seleccione" />
										</SelectTrigger>
										<SelectContent>
											<SelectItem value="No aplica">No aplica</SelectItem>
											<SelectItem value="Gestante">Gestante</SelectItem>
											<SelectItem value="Lactante">Lactante</SelectItem>
										</SelectContent>
									</Select>
									<FormMessage />
								</FormItem>
							)}
						/>
					)}
					<Button className="py-4" type="submit" disabled={loading}>
						{" "}
						{loading ? "Cargando..." : "Generar"}
					</Button>
				</form>
			</Form>
			<Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
				{isDialogOpen && (
					<DialogContent className="h-[90%] max-w-[90%] overflow-y-auto">
						<DialogTitle>{`${tipoDieta} diaria generada para ${nombre} con costo $ ${costoDieta}`}</DialogTitle>
						{responseData && (
							<>
								{tipoDieta === "Dieta de subsistencia" && (
									<div className="flex flex-col items-center">
										<a href={(responseData as CoCA).url} target="_blank" rel="noreferrer">
											<Image
												src={(responseData as CoCA).image}
												alt={(responseData as CoCA).food}
												width={200}
												height={200}
												className="mb-4"
											/>
										</a>
										<div className="flex flex-col gap-y-2 items-center">
											<a href={(responseData as CoCA).url} target="_blank" rel="noreferrer">
												<h3 className="text-lg font-bold text-center">{(responseData as CoCA).food}</h3>
											</a>
											<div className="flex flex-col items-center gap-y-2">
												<p className="text-md text-gray-700">{`Porción: ${(responseData as CoCA).quantity} gramos`}</p>
												<p className="text-md text-gray-700">{`Precio Porción: $ ${(responseData as CoCA).cost_day}`}</p>
												<p className="text-md text-gray-700">{`Precio Producto: ${(responseData as CoCA).price}`}</p>
											</div>
										</div>
									</div>
									
								)}
								{(tipoDieta === "Dieta suficiente en nutrientes" ||
									tipoDieta === "Dieta saludable") && (
									<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 py-10">
									{(responseData as CoNA).composition.map((item, index) => (
										<div key={index} className="flex flex-col items-center">
											<a href={item.url} target="_blank" rel="noreferrer">
												<div className="mb-4 w-[200px] h-[200px] flex items-center justify-center">
													<Image
														src={item.image}
														alt={item.food}
														width={200}
														height={200}
														className="object-contain"
													/>
												</div>
											</a>
											<div className="flex flex-col gap-y-2 items-center">
												<a href={item.url} target="_blank" rel="noreferrer">
													<h3 className="text-center text-lg font-bold">{item.food}</h3>
												</a>
												<div className="flex flex-col gap-y-2">
													{tipoDieta === "Dieta suficiente en nutrientes" && (
														<p className="text-md text-gray-700">{`Porción: ${item.quantity?.toFixed(2)} gramos`}</p>
													)}
													{tipoDieta === "Dieta saludable" && (
														<p className="text-md text-gray-700">{`Porción: ${(item.number_serving ? item.number_serving * 100 : 0).toFixed(2)} gramos`}</p>
													)}
													<p className="text-md text-gray-700">{`Precio Producto: ${item.price}`}</p>
												</div>
											</div>
										</div>
									))}
								</div>
								)}
							</>
						)}
						<Button onClick={() => setIsDialogOpen(false)}>Cerrar</Button>
					</DialogContent>
				)}
			</Dialog>
		</div>
	);
}
