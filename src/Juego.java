
/**
 * Clase que realiza la lógica de un juego triky de tamaño N x N para jugar contra la computadora
 * @author magoprieto
 *
 */
public class Juego {

	private int mJuego[][];
	private boolean bFinJuego = false;
	private int iTamanio;
	private int iTurno = 1;
	
	/**
	 * 
	 * @param iTamanio
	 */
	public Juego(int iTamanio) {
		this.iTamanio = iTamanio;
		mJuego = new int[iTamanio][iTamanio];
	}
	
	/**
	 * Método que evalua si un jugador hizo triky 
	 * @param iTurno
	 */
	public void evaluarJuego(int iTurno){
		this.evaluarFilas(iTurno);
		this.evaluarColumnas(iTurno);
		this.evaluarDiagonales(iTurno);
	}
	
	/**
	 * Método que evalua si hay triky en las filas de una matriz de enteros de N x N
	 * @param iTurno
	 */
	public void evaluarFilas(int iTurno){
		
		int iTriky = 0;
		
		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				if( mJuego[fila][columna] == iTurno ){
					iTriky++;	
				}
			}
			
			if(iTriky == iTamanio){
				bFinJuego = true;
			}
			
			iTriky = 0;
		}
		
		
		
	}

	/**
	 * Método que evalua si hay triky en las columnas de una matriz de enteros de N x N
	 * @param iTurno
	 */
	public void evaluarColumnas(int iTurno){

		int iTriky = 0;
		
		for(int columna=0; columna<iTamanio; columna++){
			for(int fila=0; fila<iTamanio; fila++){
				if( mJuego[fila][columna] == iTurno ){
					iTriky++;
				}
			}
			
			if(iTriky == iTamanio){
				bFinJuego = true;
			}
			
			iTriky=0;
			
		}
		

		
	}

	/**
	 * Método que evalua si hay triky en las diagonales de una matriz de enteros de N x N
	 * @param iTurno
	 */
	public void evaluarDiagonales(int iTurno){
			
		int iTriky = 0;
		
		for(int diagonal=0; diagonal<iTamanio; diagonal++){
			if( mJuego[diagonal][diagonal] == iTurno ){
				iTriky++;	
			}
		}
		
		if(iTriky == iTamanio){
			bFinJuego = true;
			return;
		}

		iTriky = 0;
				
		
		for(int diagonal=0; diagonal<iTamanio; diagonal++){
			if( mJuego[(iTamanio-1)-diagonal][diagonal] == iTurno ){
				iTriky++;	
			}
		}
		
		if(iTriky == iTamanio){
			bFinJuego = true;
			return;
		}		
		
	}

	/**
	 * Método que marca en la matriz de enteros una jugada X=1, 0=2 
	 * @param fila
	 * @param columna
	 * @param turno
	 */
	public void jugada(int fila, int columna, int turno){
		this.mJuego[fila][columna] = turno; 
	}
	
	public boolean isbFinJuego() {
		return bFinJuego;
	}

	public void setbFinJuego(boolean bFinJuego) {
		this.bFinJuego = bFinJuego;
	}

	public int getiTurno() {
		return iTurno;
	}

	public void setiTurno(int iTurno) {
		this.iTurno = iTurno;
	}

	/**
	 * Método que pide aleatoriamente una posición de una matriz y evalua si dicha posición está ocupada o no 
	 * Si encuentra que esa posición aleatoria ya ha sido ocupada, entonces buscar secuencialmente una posición
	 * vacia. 
	 * 
	 * @param iTamanio
	 * @param iTurno
	 * @return
	 */
	public PosMatris jugadaMaquinaAleatoria(int iTamanio, int iTurno){
		
		int iAleatorioFilas = (int) (Math.random()*iTamanio+1) - 1;
		int iAleatorioColumnas = (int) (Math.random()*iTamanio+1) - 1;

		if(this.mJuego[iAleatorioFilas][iAleatorioColumnas] == 0){
			this.mJuego[iAleatorioFilas][iAleatorioColumnas] = iTurno;			
			System.out.println(" Fila: "+iAleatorioFilas+" Columna: "+iAleatorioColumnas);
			return new PosMatris(iAleatorioFilas, iAleatorioColumnas);			
		}
		 
		for(int fila=0; fila<iTamanio; fila++){
			for(int columna=0; columna<iTamanio; columna++){
				if( mJuego[fila][columna] == 0 ){
					System.out.println(" Fila: "+fila+" Columna: "+columna);
					return new PosMatris(fila, columna);
				}
			}
		}
		return null;
		
	}
	
	

}
