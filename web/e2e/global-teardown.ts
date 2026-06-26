import { ssh } from './helpers/ssh'
import * as fs from 'node:fs'
import * as path from 'node:path'

const artifactRoot = process.env.PLAYWRIGHT_ARTIFACT_DIR ?? 'artifact'
const project = process.env.PLAYWRIGHT_PROJECT ?? 'desktop'

function collectArtifacts () {
  const shots = path.join(artifactRoot, `screenshots-${project}`)
  const videos = path.join(artifactRoot, `videos-${project}`)
  fs.mkdirSync(shots, { recursive: true })
  fs.mkdirSync(videos, { recursive: true })

  const resultsDir = 'test-results'
  if (!fs.existsSync(resultsDir)) return

  for (const name of fs.readdirSync(resultsDir)) {
    const dir = path.join(resultsDir, name)
    if (!fs.statSync(dir).isDirectory()) continue

    const pngs = fs.readdirSync(dir).filter((f) => f.endsWith('.png')).sort()
    pngs.forEach((png, i) => {
      const suffix = i === 0 ? '' : `-${i}`
      fs.copyFileSync(path.join(dir, png), path.join(shots, `${name}${suffix}.png`))
    })

    const video = path.join(dir, 'video.webm')
    if (fs.existsSync(video)) {
      fs.copyFileSync(video, path.join(videos, `${name}.webm`))
    }
  }
}

export default async function globalTeardown () {
  fs.mkdirSync(artifactRoot, { recursive: true })
  const journal = ssh('journalctl -u snap.files.filebrowser --no-pager | tail -800', { throw: false })
  fs.writeFileSync(path.join(artifactRoot, `filebrowser.${project}.journal.log`), journal)
  collectArtifacts()
}
