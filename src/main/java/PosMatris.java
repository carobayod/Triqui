/**
 * Clase que contiene las variables para una posición en una matriz 
 * @author carobayo
 *
 */
public class PosMatris {

	/**
	 * DECLARACIÓN DE ATRIBUTOS
	 */
	private int iFila;
	private int iColumna;

	/**
	 * MÉTODO CONSTRUCTOR DE LA CLASE
	 */
	public PosMatris() {
	}

	/**
	 * MÉTODO CONSTRUCTOR CON PARÁMETROS  
	 */
	public PosMatris(int iFila, int iColumna) {
		this.iFila = iFila ;
		this.iColumna = iColumna;
	}

	/**
	 * 
	 * Métodos de obtensión y modificación de los atributos de clase
	 */
	
	public int getiFila() {
		return iFila;
	}

	public void setiFila(int iFila) {
		this.iFila = iFila;
	}

	public int getiColumna() {
		return iColumna;
	}

	public void setiColumna(int iColumna) {
		this.iColumna = iColumna;
	}

	@Override
	public String toString() {
		return "PosMatris [iFila=" + iFila + ", iColumna=" + iColumna + "]";
	}
	
	
	
}
