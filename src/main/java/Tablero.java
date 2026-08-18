import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;


/**
 * Clase tablero - Crea y presenta la interfaz gráfica de usuario mediante una matriz de botones. 
 * Esta clase se comunica con la clase Juego que contiene toda la lógica del Juego Triky.
 * 
 * @author carobayo
 *
 */
public class Tablero extends JFrame implements ActionListener{

	private static final long serialVersionUID = 1L;
	
	private JButton mBotones[][];
	private JPanel pBotones;
	private JPanel pSur;
	private JButton bNuevoJuego;
	private JLabel lMensaje;
	private JLabel lPuntaje;
	private JComboBox<String> cbDificultad;
	private int iTamanio;	
	private Juego juego;
	private int iPuntajeJugador = 0;
	private int iPuntajeComputadora = 0;

	public Tablero(int iTamanio) {
		
		this.iTamanio = iTamanio;
		this.setTitle("Triky carobayo");

		pBotones = new JPanel();
		pBotones.setLayout(new GridLayout(iTamanio, iTamanio));

		pSur = new JPanel();
		pSur.setLayout(new BorderLayout());

		lMensaje = new JLabel("Bienvenido al juego");
		lMensaje.setHorizontalAlignment(JLabel.CENTER);
		lMensaje.setFont(new Font("Arial", Font.BOLD, 16));
		lMensaje.setForeground(Color.DARK_GRAY);

		lPuntaje = new JLabel("Jugador: 0 | Computadora: 0");
		lPuntaje.setHorizontalAlignment(JLabel.CENTER);
		lPuntaje.setFont(new Font("Arial", Font.PLAIN, 14));
		lPuntaje.setForeground(Color.GRAY);

		String[] dificultades = {"Fácil (aleatorio)", "Difícil (minimax)"};
		cbDificultad = new JComboBox<>(dificultades);
		cbDificultad.setFont(new Font("Arial", Font.PLAIN, 12));
		cbDificultad.addActionListener(this);

		bNuevoJuego = new JButton("Nuevo juego");
		bNuevoJuego.setFont(new Font("Arial", Font.BOLD, 12));
		bNuevoJuego.addActionListener(this);

		pSur.add(lPuntaje, BorderLayout.NORTH);
		pSur.add(lMensaje, BorderLayout.CENTER);
		
		JPanel pSurInferior = new JPanel();
		pSurInferior.setLayout(new BorderLayout());
		pSurInferior.add(cbDificultad, BorderLayout.WEST);
		pSurInferior.add(bNuevoJuego, BorderLayout.EAST);
		pSur.add(pSurInferior, BorderLayout.SOUTH);
		
		this.setLayout(new BorderLayout());
		mBotones = new JButton[iTamanio][iTamanio];
		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				mBotones[fila][columna] = new JButton();
				mBotones[fila][columna].setFont(new Font("Arial", Font.BOLD, 48));
				pBotones.add(mBotones[fila][columna]);
				mBotones[fila][columna].addActionListener(this);
			}
		}
		
		this.add(pBotones, BorderLayout.CENTER);
		this.add(pSur, BorderLayout.SOUTH);
		
		int iTamVentana = 150 * iTamanio;
		this.setSize(iTamVentana, iTamVentana);
		this.setMinimumSize(new Dimension(300, 300));
		this.setLocationRelativeTo(null);
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		
		init();
		
	}
	
	public void init(){
		
		lMensaje.setText("Bienvenido al juego"); 
		lMensaje.setForeground(Color.DARK_GRAY);
		
		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				mBotones[fila][columna].setText("");
				mBotones[fila][columna].setForeground(Color.BLACK);
				mBotones[fila][columna].setEnabled(true);
			}
		}
			
		juego = new Juego(iTamanio);
		
		actualizarPuntaje();
		
	}

	public static void main(String args[]){
		
		Integer iNumero = Integer.parseInt(JOptionPane.showInputDialog("Dígite el tamaño del triky (3x3, 4x4..)"));		
		Tablero t = new Tablero(iNumero);
		t.setVisible(true);
		
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		
		if(e.getSource().equals(bNuevoJuego)){
			init();
			return;
		}

		if(e.getSource().equals(cbDificultad)){
			return;
		}

		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				
				if(e.getSource().equals(mBotones[fila][columna])){
					System.out.println("Fila: "+fila+" Columna: "+columna);
					
					if(juego.getmJuego()[fila][columna] != 0) break;
					
					juego.jugada(fila, columna, juego.getiTurno());
					juego.evaluarJuego(juego.getiTurno());

					if(juego.getiTurno() == 1){
						
						mBotones[fila][columna].setText("X");
						mBotones[fila][columna].setForeground(new Color(0, 102, 204));
						
						if(juego.isbFinJuego()){
							iPuntajeJugador++;
							lMensaje.setText("Ganó el jugador! Click 'Nuevo juego'");
							lMensaje.setForeground(new Color(0, 102, 204));
							deshabilitarTablero();
							actualizarPuntaje();
							return;
						}
						
						juego.setiTurno(2);
						
						PosMatris posicionMatris;
						
						if(cbDificultad.getSelectedIndex() == 0){
							posicionMatris = juego.jugadaMaquinaAleatoria(iTamanio, juego.getiTurno());
						} else {
							posicionMatris = juego.jugadaMaquinaInteligente(iTamanio, juego.getiTurno());
						}
						
						if(posicionMatris == null){
							lMensaje.setText("Empate! Click 'Nuevo juego'");
							lMensaje.setForeground(Color.GRAY);
							deshabilitarTablero();
							return;
						}
						juego.jugada(posicionMatris.getiFila(), posicionMatris.getiColumna(), juego.getiTurno());
						juego.evaluarJuego(juego.getiTurno());
						mBotones[posicionMatris.getiFila()][posicionMatris.getiColumna()].setText("O");
						mBotones[posicionMatris.getiFila()][posicionMatris.getiColumna()].setForeground(Color.RED);
						
						if(juego.isbFinJuego()){
							iPuntajeComputadora++;
							lMensaje.setText("Ganó la computadora! Click 'Nuevo juego'");
							lMensaje.setForeground(Color.RED);
							deshabilitarTablero();
							actualizarPuntaje();
							return;
						}
						
						if(juego.isTableroLleno()){
							lMensaje.setText("Empate! Click 'Nuevo juego'");
							lMensaje.setForeground(Color.GRAY);
							deshabilitarTablero();
							return;
						}
						
						juego.setiTurno(1);
							
						
					}
					
					break;
				}
			}
		}
		
	}

	private void deshabilitarTablero(){
		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				mBotones[fila][columna].setEnabled(false);
			}
		}
	}

	private void actualizarPuntaje(){
		lPuntaje.setText("Jugador: "+iPuntajeJugador+" | Computadora: "+iPuntajeComputadora);
	}

}
