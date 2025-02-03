type CoCA = {
	food: string;
	url: string;
	image: string;
	price: string;
	quantity: number;
	demo_group: string;
	sex: number;
	group: string;
	cost_day: number;
	cost_1000kcal: number;
};

type Cost = {
	demo_group: string;
	sex: number;
	cost_day: number;
	cost_1000kcal: number;
};

type Composition = {
	food: string;
	url: string;
	image: string;
	price: string;
	quantity?: number;
	number_serving?: number;
	demo_group: string;
	sex: number;
	group: string;
};

type CoNA = {
	cost: Cost[];
	composition: Composition[];
};

type CoRD = {
	cost: Cost[];
	composition: Composition[];
};
