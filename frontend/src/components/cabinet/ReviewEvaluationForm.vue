<script setup lang="ts">
// components/cabinet/ReviewEvaluationForm.vue

const props = defineProps<{
  modelValue: {
    evaluationRating: Record<string, string>;
    languageQuality: string;
    conflictOfInterest: boolean | null;
    plagiarismDetected: boolean | null;
    ethicalIssues: boolean | null;
    articleRating: Record<string, string>;
  };
}>();

const emit = defineEmits<{
  "update:modelValue": [value: typeof props.modelValue];
}>();

const { t } = useI18n();

const EVALUATION_OPTIONS = [
  { value: "yes", label: t("reviewEvaluation.yes") },
  { value: "improve", label: t("reviewEvaluation.canImprove") },
  { value: "required", label: t("reviewEvaluation.required") },
  { value: "na", label: t("reviewEvaluation.notApplicable") },
];

const LANGUAGE_OPTIONS = [
  { value: "excellent", label: t("reviewEvaluation.languageExcellent") },
  { value: "needs_improvement", label: t("reviewEvaluation.languageNeedsImprovement") },
];

const BOOLEAN_OPTIONS = [
  { value: true, label: t("reviewEvaluation.yes") },
  { value: false, label: t("reviewEvaluation.no") },
];

const RATING_OPTIONS = [
  { value: "high", label: t("reviewEvaluation.high") },
  { value: "medium", label: t("reviewEvaluation.medium") },
  { value: "low", label: t("reviewEvaluation.low") },
  { value: "no_answer", label: t("reviewEvaluation.noAnswer") },
];

const EVALUATION_FIELDS = [
  { key: "introduction", label: t("reviewEvaluation.introduction") },
  { key: "research_design", label: t("reviewEvaluation.researchDesign") },
  { key: "methods", label: t("reviewEvaluation.methods") },
  { key: "results", label: t("reviewEvaluation.results") },
  { key: "conclusions", label: t("reviewEvaluation.conclusions") },
  { key: "figures_tables", label: t("reviewEvaluation.figuresTables") },
];

const RATING_FIELDS = [
  { key: "originality", label: t("reviewEvaluation.originality") },
  { key: "significance", label: t("reviewEvaluation.significance") },
  { key: "presentation", label: t("reviewEvaluation.presentation") },
  { key: "scientific_validity", label: t("reviewEvaluation.scientificValidity") },
  { key: "reader_interest", label: t("reviewEvaluation.readerInterest") },
];

function updateField(path: string, value: any) {
  const keys = path.split(".");
  const newValue = { ...props.modelValue };
  let current: any = newValue;
  for (let i = 0; i < keys.length - 1; i++) {
    current = current[keys[i]];
  }
  current[keys[keys.length - 1]] = value;
  emit("update:modelValue", newValue);
}
</script>

<template>
  <div class="review-evaluation">
    <h3>{{ t("reviewEvaluation.evaluationTitle") }}</h3>
    <p class="review-evaluation__hint">{{ t("reviewEvaluation.evaluationHint") }}</p>
    
    <table class="review-evaluation__table">
      <thead>
        <tr>
          <th>{{ t("reviewEvaluation.parameter") }}</th>
          <th v-for="opt in EVALUATION_OPTIONS" :key="opt.value">
            {{ opt.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="field in EVALUATION_FIELDS" :key="field.key">
          <td>{{ field.label }}</td>
          <td v-for="opt in EVALUATION_OPTIONS" :key="opt.value">
            <input
              type="radio"
              :name="`evaluation_${field.key}`"
              :value="opt.value"
              :checked="modelValue.evaluationRating[field.key] === opt.value"
              @change="updateField(`evaluationRating.${field.key}`, opt.value)"
            />
          </td>
        </tr>
      </tbody>
    </table>

    <div class="review-evaluation__field">
      <label>{{ t("reviewEvaluation.languageQuality") }}</label>
      <div class="review-evaluation__radio-group">
        <label v-for="opt in LANGUAGE_OPTIONS" :key="opt.value">
          <input
            type="radio"
            :value="opt.value"
            :checked="modelValue.languageQuality === opt.value"
            @change="updateField('languageQuality', opt.value)"
          />
          {{ opt.label }}
        </label>
      </div>
    </div>

    <div class="review-evaluation__field">
      <label>{{ t("reviewEvaluation.conflictOfInterest") }}</label>
      <div class="review-evaluation__radio-group">
        <label v-for="opt in BOOLEAN_OPTIONS" :key="String(opt.value)">
          <input
            type="radio"
            :value="opt.value"
            :checked="modelValue.conflictOfInterest === opt.value"
            @change="updateField('conflictOfInterest', opt.value)"
          />
          {{ opt.label }}
        </label>
      </div>
    </div>

    <div class="review-evaluation__field">
      <label>{{ t("reviewEvaluation.plagiarismDetected") }}</label>
      <div class="review-evaluation__radio-group">
        <label v-for="opt in BOOLEAN_OPTIONS" :key="String(opt.value)">
          <input
            type="radio"
            :value="opt.value"
            :checked="modelValue.plagiarismDetected === opt.value"
            @change="updateField('plagiarismDetected', opt.value)"
          />
          {{ opt.label }}
        </label>
      </div>
    </div>

    <div class="review-evaluation__field">
      <label>{{ t("reviewEvaluation.ethicalIssues") }}</label>
      <div class="review-evaluation__radio-group">
        <label v-for="opt in BOOLEAN_OPTIONS" :key="String(opt.value)">
          <input
            type="radio"
            :value="opt.value"
            :checked="modelValue.ethicalIssues === opt.value"
            @change="updateField('ethicalIssues', opt.value)"
          />
          {{ opt.label }}
        </label>
      </div>
    </div>

    <h3>{{ t("reviewEvaluation.articleRatingTitle") }}</h3>
    <table class="review-evaluation__table">
      <thead>
        <tr>
          <th>{{ t("reviewEvaluation.criteria") }}</th>
          <th v-for="opt in RATING_OPTIONS" :key="opt.value">
            {{ opt.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="field in RATING_FIELDS" :key="field.key">
          <td>{{ field.label }}</td>
          <td v-for="opt in RATING_OPTIONS" :key="opt.value">
            <input
              type="radio"
              :name="`rating_${field.key}`"
              :value="opt.value"
              :checked="modelValue.articleRating[field.key] === opt.value"
              @change="updateField(`articleRating.${field.key}`, opt.value)"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.review-evaluation__table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--spacing-lg);
}

.review-evaluation__table th,
.review-evaluation__table td {
  border: 1px solid var(--color-border);
  padding: var(--spacing-sm);
  text-align: center;
}

.review-evaluation__table th {
  background: var(--color-surface);
  font-weight: 600;
  font-size: var(--type-caption-size);
}

.review-evaluation__table td:first-child {
  text-align: left;
  font-weight: 500;
}

.review-evaluation__field {
  margin-bottom: var(--spacing-lg);
}

.review-evaluation__field label {
  display: block;
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
}

.review-evaluation__radio-group {
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.review-evaluation__radio-group label {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-weight: normal;
  cursor: pointer;
}

.review-evaluation__hint {
  color: var(--color-text-secondary);
  font-size: var(--type-caption-size);
  margin-bottom: var(--spacing-md);
}
</style>