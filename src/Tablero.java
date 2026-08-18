import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JFrame;
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

	/**
	 * DECLARACIÓN DE ATRIBUTOS
	 */
	private static final long serialVersionUID = 1L;
	
	private JButton mBotones[][];
	private JPanel pBotones;
	private JButton bMensaje;
	private int iTamanio;	
	private Juego juego;
	
	/**
	 * MÉTODO CONSTRUCTOR DE LA CLASE
	 */
	public Tablero(int iTamanio) {
		
		this.iTamanio = iTamanio;
		this.setTitle("Triky carobayo");

		pBotones = new JPanel();
		pBotones.setLayout(new GridLayout(iTamanio, iTamanio));
		bMensaje = new JButton("Bienvenido al juego");
		bMensaje.setEnabled(false);
		bMensaje.setForeground(Color.RED);		
		bMensaje.addActionListener(this);
		
		this.setLayout(new BorderLayout());
		mBotones = new JButton[iTamanio][iTamanio];
		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				mBotones[fila][columna] = new JButton();
				pBotones.add(mBotones[fila][columna]);
				mBotones[fila][columna].addActionListener(this);
			}
		}
		
		this.add(pBotones, BorderLayout.CENTER);
		this.add(bMensaje, BorderLayout.SOUTH);
		
		this.setSize(400, 400);
		
		init();
		
	}
	
	/**
	 * Método que limpia inicializa el juego 
	 */
	public void init(){
		
		//Mensaje en el botón
		bMensaje.setText("Bienvenido al juego"); 
		
		//Limpia matriz de botones 
		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				mBotones[fila][columna].setText("");
			}
		}
			
		//Crea una nueva clase (Juego) donde se realiza la lógica del juego 
		juego = new Juego(iTamanio);
		
		bMensaje.setEnabled(false);
		
		
	}
	/**
	 * Clase principal que ejecuta el programa
	 * @param args
	 */
	public static void main(String args[]){
		
		Integer iNumero = Integer.parseInt(JOptionPane.showInputDialog("Dígite el tamaño del triky (3x3, 4x4..)"));		
		Tablero t = new Tablero(iNumero);
		t.setVisible(true);
		
	}

	/**
	 * Clase que maneja los eventos de los elementos de la interfez gráfica
	 */
	@Override
	public void actionPerformed(ActionEvent e) {
		
		//Se recorre la matriz de botones para saber que boton se presionó
		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				
				//Se encuentra el boton presionado
				if(e.getSource().equals(mBotones[fila][columna])){
					System.out.println("Fila: "+fila+" Columna: "+columna);
					
					if(juego.getmJuego()[fila][columna] != 0) break;
					
					//Se marca en la matriz de enteros que controla el juego la jugada del jugador 1 o 2 
					juego.jugada(fila, columna, juego.getiTurno());
					//Se evalua mediante la clase juego (en la matriz de enteros) si un jugador ha ganado ya 
					juego.evaluarJuego(juego.getiTurno());

					//Juega el jugador 1 
					if(juego.getiTurno() == 1){
						
						//Se marca en la matriz de botones la X
						mBotones[fila][columna].setText("X");
						
						//Se evalua si ganó el jugador 1 (X)
						if(juego.isbFinJuego()){
							this.bMensaje.setText("Ganó el jugador "+juego.getiTurno()+" Click para jugar de nuevo" );
							bMensaje.setEnabled(true);
							return;
						}
						
						//Cambio de turno, juega la computadora
						juego.setiTurno(2);
						
						PosMatris posicionMatris;
						
						//Se obtiene la jugada de la computadora
						posicionMatris = juego.jugadaMaquinaAleatoria(iTamanio, juego.getiTurno());
						if(posicionMatris == null){
							this.bMensaje.setText("Empate! Click para jugar de nuevo");
							bMensaje.setEnabled(true);
							return;
						}
						//Se marca en la matriz de enteros que controla el juego la jugada del jugador 1 o 2
						juego.jugada(posicionMatris.getiFila(), posicionMatris.getiColumna(), juego.getiTurno());
						//Se evalua mediante la clase juego (en la matriz de enteros) si un jugador ha ganado ya
						juego.evaluarJuego(juego.getiTurno());
						//Se marca en la matriz de botones la 0
						mBotones[posicionMatris.getiFila()][posicionMatris.getiColumna()].setText("0");
						
						//Se evalua si ganó la computadora (0)
						if(juego.isbFinJuego()){
							this.bMensaje.setText("Ganó la computadora! Click para jugar de nuevo");
							bMensaje.setEnabled(true);
							return;
						}
						
						//Se evalua si hay empate
						if(juego.isTableroLleno()){
							this.bMensaje.setText("Empate! Click para jugar de nuevo");
							bMensaje.setEnabled(true);
							return;
						}
						
						//Cambio de turno, juega el humano
						juego.setiTurno(1);
							
						
					}
					
					//
//					else{
//						mBotones[fila][columna].setText("0");
//						
//						if(juego.isbFinJuego()){
//							this.bMensaje.setText("Ganó el jugador "+juego.getiTurno()+" Click para jugar de nuevo" );
//							bMensaje.setEnabled(true);
//						}
//						
//						juego.setiTurno(1);
//						
//					}
					
					break;
				}
			}
		}
		
		//Si algun jugador ha ganado, se activa el boton de mensajes para comenzar de nuevo
		if(e.getSource().equals(bMensaje)){			
			init();
		}
		
		
	}
	
	/**
	 * 
	 */
	

}
