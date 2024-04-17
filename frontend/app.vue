<template>
  <div>
    <Header />
    <UContainer class="my-5">
      <h1 class="text-2xl mb-2">Run the Algorithm</h1>

      <div class="flex space-x-4">
        <div class="w-1/2 flex space-y-4 flex-col pr-3 border-r">
          <UForm
            ref="form"
            class="space-y-4 mb-4"
            :schema="schema"
            :state="state"
            @submit="onSubmit"
          >
            <UFormGroup name="prompt" label="Prompt">
              <USelect
                v-model="state.prompt"
                :options="prompt_options"
                option-attribute="label"
                value-attribute="value"
              />
            </UFormGroup>
            <UFormGroup
              name="prompt_info"
              label="Short description of your dataset"
            >
              <UInput v-model="state.prompt_info" type="text" class="w-full" />
            </UFormGroup>
            <template
              v-if="
                state.prompt === 'metamorphic_base' ||
                state.prompt === 'metamorphic_opt'
              "
            >
              <UFormGroup name="n_aug" label="Number of Augmentations">
                <UInput
                  v-model.number="state.n_aug"
                  type="number"
                  class="w-full"
                />
              </UFormGroup>

              <UFormGroup name="robust_test" label="Robust Test">
                <USelect
                  v-model="state.robust_test"
                  :options="robust_test_options"
                  option-attribute="label"
                  value-attribute="value"
                />
              </UFormGroup>
            </template>

            <UFormGroup name="use_stats" label="Use Stats">
              <UCheckbox v-model="state.use_state" class="w-full" />
            </UFormGroup>
            <p id="input-variables">
              Input cause and effect variable name and their descriptions
            </p>
            <div class="flex space-x-4">
              <p class="flex-1">Variable name</p>
              <p class="flex-1">Description</p>
            </div>
            <div
              :key="index"
              v-for="(item, index) in state.var_name_desc"
              class="flex space-x-4"
            >
              <UFormGroup :name="`var_name_desc.${index}.name`" class="flex-2">
                <UInput v-model="state.var_name_desc[index].name"></UInput>
              </UFormGroup>
              <UFormGroup
                :name="`var_name_desc.${index}.description`"
                class="flex-1"
              >
                <UInput
                  v-model="state.var_name_desc[index].description"
                ></UInput>
              </UFormGroup>
              <UButton
                @click="removeVariable(index)"
                icon="i-heroicons-x-mark-16-solid"
                size="sm"
                color="red"
                square
                variant="solid"
              />
            </div>
            <div class="flex space-x-4 items-end">
              <UButton @click="addVariable" color="white" variant="solid"
                >Add Variable</UButton
              >
            </div>
            <div class="flex space-x-4 items-end">
              <UFormGroup label="Upload Variable from CSV">
                <UInput
                  accept=".xlsx, .xls, .csv"
                  @change="handleFileUpload"
                  type="file"
                  size="lg"
                />
              </UFormGroup>
              <UButton @click="downloadPath" variant="ghost"
                >Download Template</UButton
              >
            </div>

            <div class="space-y-2">
              <UFormGroup label="Enter CSV (optional)">
                <UInput v-model="state.csv_file" type="file" size="lg" />
              </UFormGroup>
            </div>
            <UButton :loading="spinner" type="submit" block>Run</UButton>
            <UButton type="button" @click="clear()" variant="outline" block
              >Clear</UButton
            >
          </UForm>
        </div>
        <div class="flex-1 flex justify-center items-center">
          <h1 v-if="imgResult.length == 0">Graph displays here</h1>
          <img v-else class="w-[600px]" :src="imgResult" />
        </div>
      </div>
    </UContainer>
    <UNotifications />
  </div>
</template>

<script setup lang="ts">
import { z } from "zod";
import type { FormSubmitEvent } from "#ui/types";
import readXlsxFile from "read-excel-file";

const csvInput = ref<HTMLInputElement | null>(null);
const form = ref();
const link = window;
const spinner = ref(false);
const toast = useToast();
const prompt_options = [
  {
    label: "Base",
    value: "base",
  },
  {
    label: "Optimized",
    value: "opt",
  },
  {
    label: "Metamorphic Base",
    value: "metamorphic_base",
  },
  {
    label: "Metamorphic Optimized",
    value: "metamorphic_opt",
  },
];

const robust_test_options = [
  {
    label: "Swap(randomly swap character(s) in a word)",
    value: "swap",
  },
  {
    label: "Character Delete(randomly delete character(s) in a word)",
    value: "char_delete",
  },
  {
    label: "Add Character(randomly add character(s) in a word)",
    value: "add_char",
  },
  {
    label: "Add space(randomly add space(s) in a word)",
    value: "add_space",
  },
  {
    label: "Add Number(randomly add number(s) in a word)",
    value: "add_number",
  },
  {
    label:
      "Swap with Number(randomly replace character(s) with number in a word)",
    value: "swap_with_number",
  },
  {
    label: "Synonym substitution (rephrase a word or sentence)",
    value: "synonym_sub",
  },
];
const schema = z.object({
  prompt: z.string(),
  prompt_info: z.string(),
  use_state: z.boolean(),
  robust_test: z.string().optional(),
  n_aug: z.number().optional(),
  var_name_desc: z.array(
    z.object({
      name: z.string(),
      description: z.string(),
    })
  ),
  csv_file: z.custom<File>().optional(),
});

type Schema = z.output<typeof schema>;
const imgResult = ref("");
const state = reactive({
  prompt: "base" as string | undefined,
  prompt_info: "lung disease" as string | undefined,
  use_state: false,
  n_aug: 1 as number | undefined,
  robust_test: undefined as string | undefined,
  var_name_desc: [
    {
      name: "dyspnoea" as string | undefined,
      description:
        "whether or not the patient has dyspnoea, also known as shortness of breath" as
          | string
          | undefined,
    },
    {
      name: "lung cancer" as string | undefined,
      description: "whether or not the patient has lung cancer" as
        | string
        | undefined,
    },
    {
      name: "tuberculosis" as string | undefined,
      description: "whether or not the patient has tuberculosis" as
        | string
        | undefined,
    },
  ] as { name: string; description: string }[],
  csv_file: undefined as File | undefined,
});

const addVariable = () => {
  state.var_name_desc.push({ name: undefined, description: undefined });
};

const removeVariable = (index: number) => {
  state.var_name_desc.splice(index, 1);
};

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
  spinner.value = true;
  let formattedVariables = formatVariables();
  let formData = new FormData();
  formData.append("prompt", event.data.prompt);
  formData.append("prompt_info", event.data.prompt_info);
  formData.append("use_stats", event.data.use_state ? "True" : "False");
  formData.append("n_aug", event.data.n_aug ? `${event.data.n_aug}` : "1");
  formData.append(
    "robust_test",
    event.data.robust_test ? event.data.robust_test : "swap"
  );
  formData.append("var_name_desc", JSON.stringify(formattedVariables));

  if (event.data.csv_file) {
    console.log(event.data.csv_file);
    formData.append("csv_file", event.data.csv_file);
  } else {
    formData.append("csv_file", "");
  }

  try {
    const result = (await $fetch(
      "https://causal-discovery-llm.onrender.com/cd_llm",
      {
        method: "POST",
        body: formData,
      }
    )) as any;
    imgResult.value = `data:image/png;base64, ${result.b64_result}`;
    spinner.value = false;
  } catch (error) {
    console.log(error);
    toast.add({
      title: "Unable to generate graph",
      color: "red",
    });
    spinner.value = false;
  }
};

function log() {
  console.log(form.value.validate());
}
function formatVariables() {
  const variable = {} as any;
  state.var_name_desc.forEach((item, index) => {
    variable[`var_${index + 1}`] = {
      var_name: item.name,
      var_desc: item.description,
    };
  });
  return variable;
}

const downloadPath = () => {
  const link = document.createElement("a");
  link.href = `${window.location.href}template.xlsx`;
  link.download = "variable_template.xlsx";
  link.click();
};

const clear = () => {
  form.value.clear();
  imgResult.value = "";
};

const handleFileUpload = (event: any) => {
  readXlsxFile(event.target.files[0]).then((rows) => {
    rows.forEach((row: any, index: number) => {
      if (index === 0) return;
      state.var_name_desc.push({ name: row[0], description: row[1] });
    });
  });
};
</script>


<style lang="css" scoped>
div {
  /* font-family: "Roboto", sans-serif !important; */
  font-family: "Open Sans", sans-serif !important;
}
</style>