export interface Ingredient {
  id: string;
  name: string;
}

export interface Recipe {
  title: string;
  description: string;
  cookTime: string;
  difficulty: "Easy" | "Medium" | "Hard";
  calories: number;
  ingredients: string[];
  instructions: string[];
}

export enum AppState {
  ONBOARDING = 'ONBOARDING',
  INPUT = 'INPUT',
  GENERATING = 'GENERATING',
  RESULT = 'RESULT',
  ERROR = 'ERROR'
}