<script setup lang="ts">
import { computed, ref } from 'vue'
import DaikichiResult from './components/omikuji/DaikichiResult.vue'
import ChukichiResult from './components/omikuji/ChukichiResult.vue'
import ShokichiResult from './components/omikuji/ShokichiResult.vue'
import KichiResult from './components/omikuji/KichiResult.vue'
import SuekichiResult from './components/omikuji/SuekichiResult.vue'
import KyoResult from './components/omikuji/KyoResult.vue'
import YabaiResult from './components/omikuji/YabaiResult.vue'
import AtariResult from './components/omikuji/AtariResult.vue'
import HazureResult from './components/omikuji/HazureResult.vue'
import ChukoResult from './components/omikuji/ChukoResult.vue'

type FortuneKey =
  | 'daikichi'
  | 'chukichi'
  | 'shokichi'
  | 'kichi'
  | 'suekichi'
  | 'kyo'
  | 'yabai'
  | 'atari'
  | 'hazure'
  | 'chuko'

const fortuneKeys: FortuneKey[] = [
  'daikichi',
  'chukichi',
  'shokichi',
  'kichi',
  'suekichi',
  'kyo',
  'yabai',
  'atari',
  'hazure',
  'chuko',
]

const weightedFortunes: { key: FortuneKey; weight: number }[] = [
  { key: 'daikichi', weight: 1 },
  { key: 'chukichi', weight: 1 },
  { key: 'shokichi', weight: 1 },
  { key: 'kichi', weight: 1 },
  { key: 'suekichi', weight: 1 },
  { key: 'kyo', weight: 1 },
  { key: 'yabai', weight: 1 },
  { key: 'atari', weight: 1 },
  { key: 'hazure', weight: 1 },
  { key: 'chuko', weight: 1 },
]

const fortuneComponents = {
  daikichi: DaikichiResult,
  chukichi: ChukichiResult,
  shokichi: ShokichiResult,
  kichi: KichiResult,
  suekichi: SuekichiResult,
  kyo: KyoResult,
  yabai: YabaiResult,
  atari: AtariResult,
  hazure: HazureResult,
  chuko: ChukoResult,
}

const today = new Date().toLocaleDateString('sv-SE')
const dailyStorageKey = 'omikuji:daily-result'
const currentPath = window.location.pathname.replace(/\/$/, '')
let shouldAnimateInitialResult = true

const isNoDailyPage = computed(() => currentPath.endsWith('/no-daily'))

function drawFortune(): FortuneKey {
  const totalWeight = weightedFortunes.reduce((sum, fortune) => sum + fortune.weight, 0)
  let random = Math.random() * totalWeight

  for (const fortune of weightedFortunes) {
    random -= fortune.weight

    if (random < 0) {
      return fortune.key
    }
  }

  return weightedFortunes[weightedFortunes.length - 1]!.key
}

function getDailyFortune(): FortuneKey {
  const saved = localStorage.getItem(dailyStorageKey)

  if (saved) {
    const parsed = JSON.parse(saved) as { date?: string; result?: FortuneKey }

    if (parsed.date === today && parsed.result && fortuneKeys.includes(parsed.result)) {
      shouldAnimateInitialResult = false
      return parsed.result
    }
  }

  const result = drawFortune()
  localStorage.setItem(dailyStorageKey, JSON.stringify({ date: today, result }))
  return result
}

const result = ref<FortuneKey>(isNoDailyPage.value ? drawFortune() : getDailyFortune())
const resultAnimationKey = ref(0)
const shouldAnimate = ref(isNoDailyPage.value || shouldAnimateInitialResult)

function redraw() {
  shouldAnimate.value = true
  result.value = drawFortune()
  resultAnimationKey.value += 1
}
</script>

<template>
  <main class="page">
    <section class="card">
      <p class="eyebrow">Omikuji</p>
      <h1>{{ isNoDailyPage ? '何度でも引けるおみくじ' : '今日のおみくじ' }}</h1>

      <p class="description">
        {{
          isNoDailyPage
            ? 'このページでは、ボタンを押すたびに新しい結果が出ます。'
            : 'このページでは、その日1日は同じ結果が出ます。結果はブラウザに保存されます。'
        }}
      </p>

      <component
        :is="fortuneComponents[result]"
        :key="`${result}-${resultAnimationKey}`"
        :class="{ 'fade-in': shouldAnimate }"
      />

      <button v-if="isNoDailyPage" class="button" type="button" @click="redraw">
        もう一度引く
      </button>

      <nav class="nav">
        <a href="./">今日のおみくじ</a>
        <a href="./no-daily">何度でも引く</a>
      </nav>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(255, 213, 128, 0.8), transparent 32rem),
    linear-gradient(135deg, #fff7ed, #fdf2f8);
  color: #2f1f18;
}

.card {
  width: min(100%, 720px);
  padding: 40px;
  border: 1px solid rgba(120, 53, 15, 0.16);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 24px 80px rgba(120, 53, 15, 0.18);
  text-align: center;
}

.eyebrow {
  margin: 0;
  color: #b45309;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1 {
  margin: 8px 0 12px;
  font-size: clamp(2rem, 6vw, 3.5rem);
}

.description {
  margin: 0 auto 28px;
  max-width: 34rem;
  line-height: 1.8;
  color: #6b4f43;
}

.button {
  margin-top: 28px;
  padding: 12px 24px;
  border: none;
  border-radius: 999px;
  background: #dc2626;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.button:hover {
  background: #b91c1c;
}

.nav {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 28px;
  flex-wrap: wrap;
}

.nav a {
  color: #9a3412;
  font-weight: 700;
}

.fade-in {
  animation: fade-in 0.5s ease-out;
}

@keyframes fade-in {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}
</style>
