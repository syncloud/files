import { ssh } from './helpers/ssh'
import * as fs from 'node:fs'
import * as path from 'node:path'

const artifactRoot = process.env.PLAYWRIGHT_ARTIFACT_DIR ?? 'artifact'
const label = (process.env.PLAYWRIGHT_DOMAIN ?? 'app').replace(/\.com$/, '')

function collectArtifacts () {
  const shots = path.join(artifactRoot, `screenshots-${label}`)
  const videos = path.join(artifactRoot, `videos-${label}`)
  fs.mkdirSync(shots, { recursive: true })
  fs.mkdirSync(videos, { recursive: true })

  const resultsDir = 'test-results'
  if (!fs.existsSync(resultsDir)) return

  for (const name of fs.readdirSync(resultsDir)) {
    const dir = path.join(resultsDir, name)
    if (!fs.statSync(dir).isDirectory()) continue
    for (const f of fs.readdirSync(dir)) {
      if (f.endsWith('.png')) fs.copyFileSync(path.join(dir, f), path.join(shots, f))
      if (f.endsWith('.webm')) fs.copyFileSync(path.join(dir, f), path.join(videos, `${name}.webm`))
    }
  }
}

export default async function globalTeardown () {
  fs.mkdirSync(artifactRoot, { recursive: true })
  const journal = ssh('journalctl -u snap.files.filebrowser --no-pager | tail -800', { throw: false })
  fs.writeFileSync(path.join(artifactRoot, `filebrowser.${label}.journal.log`), journal)
  collectArtifacts()
}
