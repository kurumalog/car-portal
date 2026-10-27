// car-spec-template.csv を読み込んで、車種ごとにグルーピングしたJSONを生成する
// 使い方: node scripts/build-data.js

const fs = require('fs');
const path = require('path');

const CSV_PATH = path.join(__dirname, '..', 'car-spec-template.csv');
const OUT_PATH = path.join(__dirname, '..', 'data', 'cars.json');

function parseCSVLine(line) {
  // シンプルなCSV（値の中にダブルクオート無し前提）
  return line.split(',');
}

function main() {
  const raw = fs.readFileSync(CSV_PATH, 'utf-8');
  const lines = raw.split(/\r?\n/).filter(l => l.trim().length > 0);
  const header = parseCSVLine(lines[0]);
  const rows = lines.slice(1).map(parseCSVLine);

  const idx = {};
  header.forEach((h, i) => { idx[h.trim()] = i; });

  // 車種(メーカー+車種名)単位でグルーピング
  const modelsMap = new Map();

  for (const cols of rows) {
    const maker = cols[idx['メーカー']];
    const model = cols[idx['車種']];
    const key = `${maker}___${model}`;

    if (!modelsMap.has(key)) {
      modelsMap.set(key, {
        maker,
        model,
        slug: slugify(maker + '-' + model),
        grades: []
      });
    }

    modelsMap.get(key).grades.push({
      grade: cols[idx['グレード']],
      typeCode: cols[idx['型式']],
      drive: cols[idx['駆動方式']],
      engine: cols[idx['エンジン種別']],
      displacementCc: cols[idx['排気量cc']],
      powerPs: cols[idx['出力ps']],
      priceYen: cols[idx['価格円_税込']],
      releaseDate: cols[idx['発売年月']],
      fuelEconomyWltc: cols[idx['燃費WLTC_km/L']],
      note: cols[idx['備考']] || ''
    });
  }

  const models = Array.from(modelsMap.values());

  const output = {
    generatedAt: new Date().toISOString(),
    modelCount: models.length,
    gradeCount: rows.length,
    models
  };

  fs.writeFileSync(OUT_PATH, JSON.stringify(output, null, 2), 'utf-8');
  console.log(`✔ ${models.length}車種 / ${rows.length}グレード を ${OUT_PATH} に書き出した`);
}

function slugify(s) {
  return s
    .replace(/\//g, '-')
    .replace(/\s+/g, '-')
    .replace(/[^\w\-一-龠ぁ-んァ-ヶ]/g, '');
}

main();
