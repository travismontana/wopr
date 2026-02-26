package main

import (
	"os"

	tea "charm.land/bubbletea/v2"
	"github.com/charmbracelet/lipgloss"
)

// ── styles ────────────────────────────────────────────────────────────────────

var (
	paneStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			Padding(0, 1)

	focusedPaneStyle = lipgloss.NewStyle().
				Border(lipgloss.RoundedBorder()).
				BorderForeground(lipgloss.Color("62")).
				Padding(0, 1)

	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("62"))

	buttonStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			Padding(0, 3)

	buttonFocusedStyle = buttonStyle.
				BorderForeground(lipgloss.Color("62"))
)

// ── pane index ────────────────────────────────────────────────────────────────

type pane int

const (
	paneModel pane = iota
	paneDataset
	paneParams
	paneOutput
	paneButtons
	paneCount
)

// ── model ─────────────────────────────────────────────────────────────────────

type model struct {
	focused pane
	width   int
	height  int
}

func initialModel() model {
	return model{focused: paneModel}
}

// ── init ──────────────────────────────────────────────────────────────────────

func (m model) Init() tea.Cmd {                            // ← v2: returns tea.Cmd only
	return nil
}

// ── update ────────────────────────────────────────────────────────────────────

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height

	case tea.KeyPressMsg:                                  // ← v2: KeyPressMsg not KeyMsg
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		case "tab":
			m.focused = (m.focused + 1) % paneCount
		case "shift+tab":
			m.focused = (m.focused - 1 + paneCount) % paneCount
		}
	}
	return m, nil
}

// ── view ──────────────────────────────────────────────────────────────────────

func (m model) View() tea.View {
	var v tea.View
	v.AltScreen = true

	if m.width == 0 {
		v.SetContent("loading...")    // ← SetContent, then...
		return v                      // ← return v, not the string
	}

	colW := (m.width - 6) / 3
	topH := m.height - 10

	modelPane   := m.renderPane(paneModel,   "Model",   colW, topH, "yolo11n\nyolo11s\nyolo11m")
	datasetPane := m.renderPane(paneDataset, "Dataset", colW, topH, "coco8\ncustom\nwhatever")
	paramsPane  := m.renderPane(paneParams,  "Params",  colW, topH, "epochs: 100\nbatch: 16\nimgsz: 640")

	topRow     := lipgloss.JoinHorizontal(lipgloss.Top, modelPane, datasetPane, paramsPane)
	outputPane := m.renderPane(paneOutput, "Output Path", m.width-4, 3, "/ultralytics/runs/exp1")
	trainBtn   := m.renderButton(paneButtons, "[ Train ]", true)
	cancelBtn  := m.renderButton(paneButtons, "[ Cancel ]", false)
	buttonRow  := lipgloss.JoinHorizontal(lipgloss.Top, trainBtn, cancelBtn)

	content := lipgloss.JoinVertical(lipgloss.Left, topRow, outputPane, buttonRow)
	v.SetContent(content)             // ← SetContent, then...
	return v                          // ← return v, not content
}

func (m model) renderPane(p pane, title string, w, h int, content string) string {
	s := paneStyle
	if m.focused == p {
		s = focusedPaneStyle
	}
	inner := titleStyle.Render(title) + "\n" + content
	return s.Width(w).Height(h).Render(inner)
}

func (m model) renderButton(p pane, label string, primary bool) string {
	if m.focused == p && primary {
		return buttonFocusedStyle.Render(label)
	}
	return buttonStyle.Render(label)
}

// ── main ──────────────────────────────────────────────────────────────────────

func main() {
	p := tea.NewProgram(initialModel())  // ← v2: WithAltScreen() confirmed
	if _, err := p.Run(); err != nil {
		os.Exit(1)
	}
}