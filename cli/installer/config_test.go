package installer

import (
	"os"
	"path"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/syncloud/golib/config"
)

func TestConfigTemplatesRender(t *testing.T) {
	out := t.TempDir()
	variables := Variables{
		App:            App,
		AppDir:         AppDir,
		DataDir:        DataDir,
		CommonDir:      CommonDir,
		StorageDir:     "/data/files",
		AuthUrl:        "https://auth.example.com",
		AppUrl:         "https://files.example.com",
		ClientId:       App,
		ClientSecret:   "secret",
		AdminGroup:     AdminGroup,
		Socket:         path.Join(DataDir, "filebrowser.sock"),
		DatabaseSqlite: path.Join(DataDir, "filebrowser.sqlite"),
		CacheDir:       path.Join(DataDir, "cache"),
	}

	err := config.Generate("../../config", out, variables)
	assert.NoError(t, err)

	nginx, err := os.ReadFile(path.Join(out, "nginx.conf"))
	assert.NoError(t, err)
	assert.Contains(t, string(nginx), "listen unix:/var/snap/files/common/web.socket;")
	assert.Contains(t, string(nginx), "server unix:/var/snap/files/current/filebrowser.sock;")

	filebrowser, err := os.ReadFile(path.Join(out, "config.yaml"))
	assert.NoError(t, err)
	assert.Contains(t, string(filebrowser), `socket: "/var/snap/files/current/filebrowser.sock"`)
	assert.Contains(t, string(filebrowser), `issuerUrl: "https://auth.example.com"`)
	assert.Contains(t, string(filebrowser), `path: "/data/files"`)
	assert.NotContains(t, string(filebrowser), "{{")
}
