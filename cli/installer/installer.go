package installer

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	cp "github.com/otiai10/copy"
	"github.com/syncloud/golib/config"
	"github.com/syncloud/golib/linux"
	"github.com/syncloud/golib/platform"
	"go.uber.org/zap"
	"os"
	"path"
)

type Variables struct {
	App          string
	AppDir       string
	DataDir      string
	CommonDir    string
	StorageDir   string
	AuthUrl      string
	AppUrl       string
	ClientId     string
	ClientSecret string
	AdminGroup   string
	Key          string
	Socket       string
	Database     string
	CacheDir     string
}

const (
	App        = "files"
	AppDir     = "/snap/files/current"
	DataDir    = "/var/snap/files/current"
	CommonDir  = "/var/snap/files/common"
	AdminGroup = "syncloud"
)

type Installer struct {
	newVersionFile     string
	currentVersionFile string
	platformClient     *platform.Client
	installFile        string
	keyFile            string
	logger             *zap.Logger
}

func New(logger *zap.Logger) *Installer {
	return &Installer{
		newVersionFile:     path.Join(AppDir, "version"),
		currentVersionFile: path.Join(DataDir, "version"),
		platformClient:     platform.New(),
		installFile:        path.Join(CommonDir, "installed"),
		keyFile:            path.Join(DataDir, "jwt.key"),
		logger:             logger,
	}
}

func (i *Installer) Install() error {
	return i.UpdateConfigs()
}

func (i *Installer) Configure() error {
	if i.IsInstalled() {
		return i.Upgrade()
	}
	return i.Initialize()
}

func (i *Installer) IsInstalled() bool {
	_, err := os.Stat(i.installFile)
	return err == nil
}

func (i *Installer) Initialize() error {
	if err := i.StorageChange(); err != nil {
		return err
	}
	if err := os.WriteFile(i.installFile, []byte("installed"), 0644); err != nil {
		return err
	}
	return i.UpdateVersion()
}

func (i *Installer) Upgrade() error {
	if err := i.StorageChange(); err != nil {
		return err
	}
	return i.UpdateVersion()
}

func (i *Installer) PreRefresh() error {
	return nil
}

func (i *Installer) PostRefresh() error {
	if err := i.UpdateConfigs(); err != nil {
		return err
	}
	if err := i.ClearVersion(); err != nil {
		return err
	}
	return i.FixPermissions()
}

func (i *Installer) AccessChange() error {
	return i.UpdateConfigs()
}

func (i *Installer) StorageChange() error {
	storageDir, err := i.platformClient.InitStorage(App, App)
	if err != nil {
		return err
	}
	return linux.Chown(storageDir, App)
}

func (i *Installer) ClearVersion() error {
	return os.RemoveAll(i.currentVersionFile)
}

func (i *Installer) UpdateVersion() error {
	return cp.Copy(i.newVersionFile, i.currentVersionFile)
}

func (i *Installer) UpdateConfigs() error {
	if err := linux.CreateUser(App); err != nil {
		return err
	}
	if err := i.StorageChange(); err != nil {
		return err
	}
	if err := linux.CreateMissingDirs(
		path.Join(DataDir, "config"),
		path.Join(DataDir, "nginx"),
		path.Join(DataDir, "cache"),
	); err != nil {
		return err
	}

	storageDir, err := i.platformClient.InitStorage(App, App)
	if err != nil {
		return err
	}
	if err := i.GenerateConfig(storageDir); err != nil {
		return fmt.Errorf("generate config: %w", err)
	}

	return i.FixPermissions()
}

func (i *Installer) GenerateConfig(storageDir string) error {
	secret, err := i.platformClient.RegisterOIDCClient(App, "/api/auth/oidc/callback", false, "client_secret_basic")
	if err != nil {
		return fmt.Errorf("oidc register: %w", err)
	}
	authUrl, err := i.platformClient.GetAppUrl("auth")
	if err != nil {
		return err
	}
	appUrl, err := i.platformClient.GetAppUrl(App)
	if err != nil {
		return err
	}
	key, err := i.SigningKey()
	if err != nil {
		return err
	}

	variables := Variables{
		App:          App,
		AppDir:       AppDir,
		DataDir:      DataDir,
		CommonDir:    CommonDir,
		StorageDir:   storageDir,
		AuthUrl:      authUrl,
		AppUrl:       appUrl,
		ClientId:     App,
		ClientSecret: secret,
		AdminGroup:   AdminGroup,
		Key:          key,
		Socket:       path.Join(DataDir, "filebrowser.sock"),
		Database:     path.Join(DataDir, "database.db"),
		CacheDir:     path.Join(DataDir, "cache"),
	}

	return config.Generate(
		path.Join(AppDir, "config"),
		path.Join(DataDir, "config"),
		variables,
	)
}

func (i *Installer) SigningKey() (string, error) {
	existing, err := os.ReadFile(i.keyFile)
	if err == nil && len(existing) > 0 {
		return string(existing), nil
	}
	buf := make([]byte, 32)
	if _, err := rand.Read(buf); err != nil {
		return "", err
	}
	key := hex.EncodeToString(buf)
	if err := os.WriteFile(i.keyFile, []byte(key), 0640); err != nil {
		return "", err
	}
	return key, nil
}

func (i *Installer) FixPermissions() error {
	if err := linux.Chown(DataDir, App); err != nil {
		return err
	}
	return linux.Chown(CommonDir, App)
}

func (i *Installer) BackupPreStop() error    { return i.PreRefresh() }
func (i *Installer) RestorePreStart() error  { return i.PostRefresh() }
func (i *Installer) RestorePostStart() error { return i.Configure() }
